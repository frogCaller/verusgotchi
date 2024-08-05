import sys
import os
import json
import time
import requests
import subprocess
import socket
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from waveshare_epd import epd2in13_V3
from PIL import Image, ImageDraw, ImageFont
import faces
import psutil

#########################################################
##  ADD YOUR VERUS WALLET AND A NAME FOR YOUR GOTCHI!  ##
#########################################################
username = "verusgotchi"
my_Verus_Wallet = "YOUR_VERUS_WALLET_HERE"


# Screen rotation
screen_rotate = 0

# Verus API URL
verus_url = "https://luckpool.net/verus/miner/" + my_Verus_Wallet

# Data directory
data_directory = "Data"
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# Historical data file
historical_prices_file = os.path.join(data_directory, "verus_historical_prices.json")

# List to store faces for different conditions
myface = []
quotes_list = []

last_quote_update_time = 0
current_quote = ""
first_run = True
last_price_fetch_time = 0
last_graph_display_time = time.time() - 120

def get_verus_data(verus_url):
    try:
        response = requests.get(verus_url)
        response.raise_for_status()
        data = response.json()
        return {
            "hashrate": data.get("hashrateString", "N/A"),
            "balance": data.get("balance", "N/A"),
            "paid": data.get("paid", "N/A"),
            "workers": len(data.get("workers", [])),
            "estimatedLuck": data.get("estimatedLuck", "N/A")  # Added estimatedLuck
        }
    except requests.RequestException as e:
        print(f"Error fetching Verus data: {e}")
        return None

def fetch_coin_price():
    try:
        # Fetching the data from the new URL
        stats_url = "https://luckpool.net/verus/stats"
        response = requests.get(stats_url)
        response.raise_for_status()
        data = response.json()

        # Extracting the Verus Coin price
        price = data["marketStats"]["price_usd"]
        save_price_to_file(price)

        # Extracting the network hash rate
        network_hashrate = data["networkStats"]["hashrateString"]

        return price, network_hashrate
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, "N/A"

def save_price_to_file(price):
    with open(os.path.join(data_directory, "verus_price.txt"), "w") as file:
        file.write(str(price))

def read_price_from_file():
    try:
        with open(os.path.join(data_directory, "verus_price.txt"), "r") as file:
            price = float(file.read().strip())
        return price
    except (FileNotFoundError, ValueError):
        return None

def get_cpu_memory_usage():
    cpu_usage = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    return cpu_usage, memory_usage

# Function to read quotes from quotes.txt
def read_quotes():
    global quotes_list
    try:
        with open("quotes.txt", "r") as file:
            quotes_list = file.readlines()
        quotes_list = [quote.strip() for quote in quotes_list if quote.strip()] 
    except FileNotFoundError:
        print("quotes.txt file not found.")

# Function to get a new quote every 10 seconds
def get_new_quotes():
    global current_quote, first_run
    if first_run:
        first_run = False
        current_quote = "New day, new coin"
    elif quotes_list:
        # Select one random quote from the list
        current_quote = random.choice(quotes_list)
    else:
        current_quote = "No quotes available"
    return current_quote

# Initial call to read quotes from the file
read_quotes()

# Function to get the current time
def get_current_time():
    now = datetime.now()
    day = now.strftime("%A").upper()
    date = now.strftime("%m/%d/%y")
    time_str = now.strftime("%I:%M %p")
    return f"{day}  {time_str}\n{date}"

# Function to get CPU temperature
def get_cpu_temperature():
    try:
        cpu_temp = os.popen("vcgencmd measure_temp").readline()
        return cpu_temp.replace("temp=", "").replace("'","°")
    except:
        return False

# Function to get Wi-Fi status
def get_wifi_status():
    try:
        subprocess.check_output(['ping', '-c', '1', '8.8.8.8'])
        return "WIFI: OK"
    except subprocess.CalledProcessError:
        return "NET ERROR"

def update_face(verus_data, first_run):
    global myface

    # Reset the face list
    myface.clear()
    wifi_status = get_wifi_status()
    cpu_temp = get_cpu_temperature()
    cpu_temp_value = float(cpu_temp.replace("°C", "")) if cpu_temp else None

    # Determine face based on conditions
    if wifi_status == "NET ERROR":
        myface.append(faces.SAD)
    elif verus_data["hashrate"] == "0.00 H/s":
        myface.append(faces.BORED)
    elif cpu_temp_value and cpu_temp_value >= 72:
        current_time = int(time.time())
        if current_time % 2 == 0:
            myface.append(faces.HOT)
        else:
            myface.append(faces.HOT2)
    elif verus_data["hashrate"] != "0.00 H/s":
        if first_run:
            myface.append(faces.AWAKE)
        else:
            current_time = int(time.time())
            state = current_time // 3 % 17  # 17 states excluding COOL
            if state in [0, 1, 2, 3]:  # LOOK_L twice
                myface.append(faces.LOOK_R)
            elif state in [4, 5, 6, 7]:  # LOOK_R twice
                myface.append(faces.LOOK_L)
            elif state in [8]:  # AWAKE twice
                myface.append(faces.SLEEP)
            elif state in [9, 10, 11, 12]:  # LOOK_L_HAPPY four times
                myface.append(faces.LOOK_R_HAPPY)
            elif state in [13, 14, 15, 16]:  # LOOK_R_HAPPY four times
                myface.append(faces.LOOK_L_HAPPY)
            else:  # Additional states to add more variety
                myface.append(faces.HAPPY)
    else:
        myface.append(faces.HAPPY)  # Default happy face

# Function to get historical prices from CoinGecko
def get_historical_prices():
    url = f"https://api.coingecko.com/api/v3/coins/verus-coin/market_chart?vs_currency=usd&days={7}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        prices = [price[1] for price in data["prices"]]
        return prices
    except requests.RequestException as e:
        print(f"Error fetching historical prices: {e}")
        return []

# Function to save historical prices to a file
def save_historical_prices(prices):
    with open(historical_prices_file, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "prices": prices}, f)

# Function to load historical prices from a file
def load_historical_prices():
    if os.path.exists(historical_prices_file):
        with open(historical_prices_file, "r") as f:
            data = json.load(f)
            return data["timestamp"], data["prices"]
    return None, None

# Function to check if new historical data should be fetched
def should_fetch_new_historical_data(timestamp):
    if timestamp:
        last_fetch_time = datetime.fromisoformat(timestamp)
        return datetime.now() - last_fetch_time >= timedelta(minutes=5)
    return True

# Function to fetch historical prices with caching
def fetch_historical_prices_with_cache():
    timestamp, cached_prices = load_historical_prices()
    if should_fetch_new_historical_data(timestamp):
        # Fetch new data if needed
        new_prices = get_historical_prices()
        if new_prices:
            save_historical_prices(new_prices)
            return new_prices
        return cached_prices
    return cached_prices

# Function to plot prices
def plot_prices(prices):
    # Define the desired dimensions in pixels
    top_left_x, top_left_y = 5, 30
    bottom_right_x, bottom_right_y = 145, 75

    # Calculate the width and height in pixels
    width_pixels = bottom_right_x - top_left_x
    height_pixels = bottom_right_y - top_left_y

    # Convert pixel dimensions to inches (assuming 100 DPI)
    dpi = 100
    width_inches = width_pixels / dpi
    height_inches = height_pixels / dpi

    # Adjust figure size to fit the specified area
    plt.figure(figsize=(width_inches, height_inches))
    ax = plt.gca()
    ax.plot(prices, color='black')

    # Set the y-axis limits to the range of the prices
    ax.set_ylim([min(prices), max(prices)])

    # Remove axis labels and plot borders
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')  # Remove all axes
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Save the plot to an image file in the Data folder
    plot_path = os.path.join(data_directory, "VRSC_plot.png")
    plt.savefig(plot_path, dpi=dpi, bbox_inches='tight', pad_inches=0)
    plt.close()
    return plot_path

def display_verus_data(epd, verus_data, verus_price, network_hashrate, cpu_temp, cpu_usage, memory_usage, show_graph=False):
    global current_quote  # Use the global current_quote
    
    font10 = ImageFont.truetype('Font.ttc', 10)
    font12 = ImageFont.truetype('Font.ttc', 12)
    font15 = ImageFont.truetype('Font.ttc', 15)
    face32 = ImageFont.truetype(('DejaVuSansMono.ttf'), 32)

    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)

    # Drawing the template
    draw.rectangle((0, 0, 250, 122), fill=255)
    draw.text((2, 1), f"VERUS COIN", font=font10, fill=0)
    draw.text((80, 1), get_wifi_status(), font=font10, fill=0)

    draw.text((135, 1), "MINER: ON" if verus_data["hashrate"] != "0.00 H/s" else "MINER: OFF", font=font10, fill=0)
    draw.text((200, 1), datetime.now().strftime("%-I:%M %p"), font=font10, fill=0)
    draw.line([(0, 13), (250, 13)], fill=0, width=1)
    
    draw.text((5, 15), f"{username}>", font=font12, fill=0)

    # Update current_quote if CPU temperature is too high
    if myface and myface[0] == faces.HOT:
        current_quote = "It's getting hot!"
        
    # Display Verus price
    if verus_price is not None:
        draw.text((5, 70), f"Price: ${verus_price:.3f}", font=font15, fill=0)
    else:
        draw.text((5, 70), "Price: N/A", font=font15, fill=0)
    draw.text((5, 88), f"Network: {network_hashrate}/s", font=font12, fill=0)
    # Display new quotes
    draw.text((125, 55), current_quote, font=font12, fill=0)

    # Draw the balance text with the chosen font
    draw.text((125, 17), f"{verus_data['balance']} VRSC", font=font15, fill=0)
    draw.text((125, 37), f"{verus_data['hashrate']}/s", font=font12, fill=0)
    
    draw.line([(0, 108), (250, 108)], fill=0, width=1)
    
    # Calculate positions based on text widths using textbbox
    label_y = 75  # Starting y position
    value_y = 85  # Starting y position for values
    label_x = 140  # Starting x position for labels
    spacing = 10  # Spacing between labels and values

    # Get the width of each label
    mem_label_width = draw.textbbox((0, 0), "mem", font=font10)[2]
    cpu_label_width = draw.textbbox((0, 0), "cpu", font=font10)[2]
    temp_label_width = draw.textbbox((0, 0), "temp", font=font10)[2]

    # Calculate x positions for labels
    cpu_label_x = label_x + mem_label_width + spacing
    temp_label_x = cpu_label_x + cpu_label_width + spacing

    # Calculate x positions for values
    mem_value_x = label_x
    cpu_value_x = cpu_label_x
    temp_value_x = temp_label_x

    # Draw labels horizontally
    draw.text((label_x, label_y), "mem", font=font10, fill=0)
    draw.text((cpu_label_x, label_y), "cpu", font=font10, fill=0)
    draw.text((temp_label_x, label_y), "temp", font=font10, fill=0)

    # Draw values horizontally
    draw.text((mem_value_x, value_y), f"{memory_usage:.1f}%", font=font10, fill=0)
    draw.text((cpu_value_x, value_y), f"{cpu_usage:.0f}%", font=font10, fill=0)
    draw.text((temp_value_x, value_y), f"{cpu_temp}", font=font10, fill=0)

    # Display number of workers and paid balance
    draw.text((2, 110), f"Workers: {verus_data['workers']}", font=font10, fill=0)
    draw.text((65, 110), f"Paid: {verus_data['paid']:,.3f} VRSC", font=font10, fill=0)
    draw.text((160, 110), f"Luck: {verus_data['estimatedLuck']}", font=font10, fill=0)

    if show_graph:
        # Plot historical prices and load the plot image
        historical_prices = fetch_historical_prices_with_cache()
        plot_path = plot_prices(historical_prices)
        plot_image = Image.open(plot_path).convert('1')
        image.paste(plot_image, (5, 35)) 

    else:
        # Display current face
        if myface:
            draw.text((3, 28), myface[0], font=face32, fill=0)

    # Rotate and display the image    
    image = image.rotate(screen_rotate)
    epd.displayPartial(epd.getbuffer(image))

def main():
    global last_price_fetch_time, last_graph_display_time  # Declare the variables as global
    last_face_display_time = time.time()  # Initialize with the current time
    
    epd = epd2in13_V3.EPD()
    epd.init()
    epd.Clear(0xFF)

    last_fetch_time = 0
    last_face_update_time = 0
    last_quote_update_time = 0
    last_cpu_temp_update_time = 0
    verus_data = None
    verus_price = None
    network_hashrate = None
    cpu_temp = None 
    cpu_usage = None
    memory_usage = None
    first_run = True 
    show_graph = False  # Variable to control graph display

    while True:
        current_time = time.time()
        
        if current_time - last_cpu_temp_update_time >= 3:
            cpu_temp = get_cpu_temperature()
            cpu_usage, memory_usage = get_cpu_memory_usage()  # Get CPU and memory usage
            last_cpu_temp_update_time = current_time
        
        # Fetch Verus Coin data every 60 seconds
        if current_time - last_fetch_time >= 60:
            verus_data = get_verus_data(verus_url)
            last_fetch_time = current_time

        # Fetch Verus Coin price every 5 minutes
        if current_time - last_price_fetch_time >= 300:
            verus_price, network_hashrate = fetch_coin_price()
            last_price_fetch_time = current_time
        else:
            verus_price = read_price_from_file()
            network_hashrate = network_hashrate if 'network_hashrate' in locals() else "N/A"

        # Check if it's time to switch between faces and graph
        if not show_graph and (current_time - last_face_display_time >= 60):
            # Time to display the graph
            show_graph = True
            last_graph_display_time = current_time

        if show_graph:
            if current_time - last_graph_display_time >= 30:
                # Time to switch back to faces
                show_graph = False
                last_face_display_time = current_time
            else:
                display_verus_data(epd, verus_data, verus_price, network_hashrate, cpu_temp, cpu_usage, memory_usage, show_graph=True)
        else:
            display_verus_data(epd, verus_data, verus_price, network_hashrate, cpu_temp, cpu_usage, memory_usage, show_graph=False)
            # Update face every 2 seconds
            if current_time - last_face_update_time >= 3:
                if verus_data:
                    update_face(verus_data, first_run) 
                    first_run = False  
                last_face_update_time = current_time

            # Update quotes every 10 seconds
            if current_time - last_quote_update_time >= 10:
                current_quote = get_new_quotes() 
                last_quote_update_time = current_time

        time.sleep(3)


if __name__ == "__main__":
    main()
