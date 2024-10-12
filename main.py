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
import psutil

#########################################################
##  ADD YOUR VERUS WALLET AND A NAME FOR YOUR GOTCHI!  ##
#########################################################
username = "verusgotchi"
my_Verus_Wallet = "YOUR_VERUS_WALLET_HERE"

LOOK_R = '( ⚆_⚆)'
LOOK_L = '(☉_☉ )'
LOOK_R_HAPPY = '( ◕‿◕)'
LOOK_L_HAPPY = '(◕‿◕ )'
SLEEP = '(⇀‿‿↼)'
SLEEP2 = '(≖‿‿≖)'
AWAKE = '(◕‿‿◕)'
BORED = '(-__-)'
INTENSE = '(°▃▃°)'
COOL = '(⌐■_■)'
HAPPY = '(•‿‿•)'
GRATEFUL = '(^‿‿^)'
EXCITED = '(ᵔ◡◡ᵔ)'
MOTIVATED = '(☼‿‿☼)'
DEMOTIVATED = '(≖__≖)'
SMART = '(✜‿‿✜)'
LONELY = '(ب__ب)'
SAD = '(╥ ╥ )'
ANGRY = "(-_-')"
HOT = "(☉_☉')"
HOT2 = "('☉_☉)"
FRIEND = '(♥‿‿♥)'
BROKEN = '(☓‿‿☓)'
DEBUG = '(#__#)'
UPLOAD = '(1__0)'
UPLOAD1 = '(1__1)'

# Screen rotation
screen_rotate = 180

# Verus API URL
verus_url = "https://luckpool.net/verus/miner/" + my_Verus_Wallet

# Data directory
data_directory = "Data"
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# Historical data file
historical_prices_file = os.path.join(data_directory, "verus_historical_prices.json")

myface = []
quotes_list = []

balances = []
timestamps = []
hourly_average_balance = None

last_quote_update_time = 0
current_quote = ""
first_run = True
last_price_fetch_time = 0
last_graph_display_time = time.time() - 120

def fetch_verus_rank():
    try:
        coingecko_url = "https://api.coingecko.com/api/v3/coins/verus-coin"
        response = requests.get(coingecko_url)
        response.raise_for_status()
        data = response.json()
        return data.get("market_data", {}).get("market_cap_rank", "N/A")
    except requests.RequestException as e:
        print(f"Error fetching Verus rank: {e}")
        return "N/A"
      
def get_verus_data(verus_url):
    try:
        response = requests.get(verus_url)
        response.raise_for_status()
        data = response.json()
        
        # Fetch the rank from CoinGecko
        verus_rank = fetch_verus_rank()

        return {
            "hashrate": data.get("hashrateString", "N/A"),
            "balance": data.get("balance", "N/A"),
            "paid": data.get("paid", "N/A"),
            "workers": len(data.get("workers", [])),
            "rank": verus_rank,
            "estimatedLuck": data.get("estimatedLuck", "N/A") 
        }
    except requests.RequestException as e:
        print(f"Error fetching Verus data: {e}")
        return {
            "hashrate": "N/A",
            "balance": "N/A",
            "paid": "N/A",
            "rank": "N/A",
            "workers": 0,
            "estimatedLuck": "N/A"
        }
        
def fetch_coin_price():
    try:
        stats_url = "https://luckpool.net/verus/stats"
        response = requests.get(stats_url)
        response.raise_for_status()
        data = response.json()

        price = data["marketStats"]["price_usd"]
        manage_price_file(price)

        network_hashrate = data["networkStats"]["hashrateString"]
        return price, network_hashrate
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, "N/A"

def manage_price_file(price=None):
    file_path = os.path.join(data_directory, "verus_price.txt")
    if price is not None:
        with open(file_path, "w") as file:
            file.write(str(price))
    else:
        try:
            with open(file_path, "r") as file:
                return float(file.read().strip())
        except (FileNotFoundError, ValueError):
            return None

def get_cpu_memory_usage():
    cpu_usage = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    return cpu_usage, memory_usage

def read_quotes():
    global quotes_list
    try:
        with open("quotes.txt", "r") as file:
            quotes_list = file.readlines()
        quotes_list = [quote.strip() for quote in quotes_list if quote.strip()] 
    except FileNotFoundError:
        print("quotes.txt file not found.")

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

read_quotes()

def get_current_time():
    now = datetime.now()
    day = now.strftime("%A").upper()
    date = now.strftime("%m/%d/%y")
    time_str = now.strftime("%I:%M %p")
    return f"{day}  {time_str}\n{date}"
  
def get_expense_indicator(now):
    current_day = now.weekday()  # Monday is 0 and Sunday is 6
    current_hour = now.hour

    if current_day < 5:  # Monday to Friday
        if (0 <= current_hour < 6) or (10 <= current_hour < 14):
            return "$$$"
        elif (6 <= current_hour < 10) or (14 <= current_hour < 16) or (21 <= current_hour < 24):
            return "$$"
        else:
            return "$"
    else:  # Saturday and Sunday
        if (0 <= current_hour < 14):
            return "$$$"
        elif (14 <= current_hour < 16) or (21 <= current_hour < 24):
            return "$$"
        else:
            return "$"

def get_cpu_temperature():
    try:
        cpu_temp = os.popen("vcgencmd measure_temp").readline()
        return cpu_temp.replace("temp=", "").replace("'","°")
    except:
        return False

def get_wifi_status():
    try:
        subprocess.check_output(['ping', '-c', '1', '8.8.8.8'])
        return "WIFI: OK"
    except subprocess.CalledProcessError:
        return "NET ERROR"

def update_face(verus_data, first_run):
    global myface

    myface.clear()
    wifi_status = get_wifi_status()
    cpu_temp = get_cpu_temperature()
    cpu_temp_value = float(cpu_temp.replace("°C", "")) if cpu_temp else None

    if wifi_status == "NET ERROR":
        myface.append(SAD)
    elif verus_data["hashrate"] == "0.00 H/s":
        myface.append(BORED)
    elif cpu_temp_value and cpu_temp_value >= 72:
        current_time = int(time.time())
        if current_time % 2 == 0:
            myface.append(HOT)
        else:
            myface.append(HOT2)
    elif verus_data["hashrate"] != "0.00 H/s":
        if first_run:
            myface.append(AWAKE)
        else:
            current_time = int(time.time())
            state = current_time // 3 % 17
            if state in [0, 1, 2, 3]:
                myface.append(LOOK_R)
            elif state in [4, 5, 6, 7]: 
                myface.append(LOOK_L)
            elif state in [8]:
                myface.append(SLEEP)
            elif state in [9, 10, 11, 12]:
                myface.append(LOOK_R_HAPPY)
            elif state in [13, 14, 15, 16]:
                myface.append(LOOK_L_HAPPY)
            else: 
                myface.append(HAPPY)
    else:
        myface.append(HAPPY)

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

def save_historical_prices(prices):
    with open(historical_prices_file, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "prices": prices}, f)

def load_historical_prices():
    if os.path.exists(historical_prices_file):
        with open(historical_prices_file, "r") as f:
            data = json.load(f)
            return data["timestamp"], data["prices"]
    return None, None

def should_fetch_new_historical_data(timestamp):
    if timestamp:
        last_fetch_time = datetime.fromisoformat(timestamp)
        return datetime.now() - last_fetch_time >= timedelta(minutes=5)
    return True

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

def plot_prices(prices):
    top_left_x, top_left_y = 5, 30
    bottom_right_x, bottom_right_y = 145, 75

    width_pixels = bottom_right_x - top_left_x
    height_pixels = bottom_right_y - top_left_y

    dpi = 100
    width_inches = width_pixels / dpi
    height_inches = height_pixels / dpi

    plt.figure(figsize=(width_inches, height_inches))
    ax = plt.gca()
    ax.plot(prices, color='black')

    ax.set_ylim([min(prices), max(prices)])

    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    plot_path = os.path.join(data_directory, "VRSC_plot.png")
    plt.savefig(plot_path, dpi=dpi, bbox_inches='tight', pad_inches=0)
    plt.close()
    return plot_path

def calculate_hourly_average():
    global balances, timestamps, hourly_average_balance
    if len(balances) > 1:
        total_balance_change = 0
        total_time_elapsed = 0
        for i in range(1, len(balances)):
            balance_change = balances[i] - balances[i - 1]
            if balances[i] < balances[i - 1]:
                balance_change = balances[i]
            time_elapsed = (timestamps[i] - timestamps[i - 1]) / 60 
            total_balance_change += balance_change
            total_time_elapsed += time_elapsed
        
        if total_time_elapsed > 0:
            hourly_average_balance = (total_balance_change / total_time_elapsed) * 60 
        else:
            hourly_average_balance = None
            
def header_info(draw, verus_data, now, font, screen_width=250):
    coin_text = "VERUS COIN"
    rank_text = f"RANK: {verus_data['rank']}"
    expense_indicator = get_expense_indicator(now)
    time_text = datetime.now().strftime("%-I:%M %p")

    coin_text_width = draw.textbbox((0, 0), coin_text, font=font)[2]
    rank_text_width = draw.textbbox((0, 0), rank_text, font=font)[2]
    expense_text_width = draw.textbbox((0, 0), expense_indicator, font=font)[2]
    time_text_width = draw.textbbox((0, 0), time_text, font=font)[2]

    total_text_width = coin_text_width + rank_text_width + expense_text_width + time_text_width

    available_space = screen_width - total_text_width
    if available_space > 0:
        spacing = max(5, available_space // 3)
    else:
        spacing = 5

    x_coin = 5
    x_rank = x_coin + coin_text_width + spacing
    x_expense = x_rank + rank_text_width + spacing
    x_time = min(screen_width - time_text_width - 5, x_expense + expense_text_width + spacing)

    draw.text((x_coin, 1), coin_text, font=font, fill=0)
    draw.text((x_rank, 1), rank_text, font=font, fill=0)
    draw.text((x_expense, 1), expense_indicator, font=font, fill=0)
    draw.text((x_time, 1), time_text, font=font, fill=0)

            
def footer_info(draw, verus_data, font, screen_width=250):
    workers_text = f"Workers: {verus_data['workers']}"
    paid_text = f"Paid: {verus_data['paid']:,.2f} VRSC"
    luck_text = f"Luck: {verus_data['estimatedLuck']}"

    workers_text_width = draw.textbbox((0, 0), workers_text, font=font)[2]
    paid_text_width = draw.textbbox((0, 0), paid_text, font=font)[2]
    luck_text_width = draw.textbbox((0, 0), luck_text, font=font)[2]

    x_workers = 5

    x_luck = screen_width - luck_text_width - 5

    x_paid = (x_workers + workers_text_width + x_luck - paid_text_width) // 2

    draw.text((x_workers, 110), workers_text, font=font, fill=0)
    draw.text((x_paid, 110), paid_text, font=font, fill=0)
    draw.text((x_luck, 110), luck_text, font=font, fill=0)

def display_verus_data(epd, verus_data, verus_price, network_hashrate, cpu_temp, cpu_usage, memory_usage, now, show_graph=False):
    global current_quote
    global hourly_average_balance
    
    font10 = ImageFont.truetype('Fonts/Font.ttc', 10)
    font12 = ImageFont.truetype('Fonts/Font.ttc', 12)
    font15 = ImageFont.truetype('Fonts/Font.ttc', 15)
    face32 = ImageFont.truetype(('Fonts/DejaVuSansMono.ttf'), 32)

    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, 250, 122), fill=255)
    header_info(draw, verus_data, now, font10, screen_width=250)
    
    draw.line([(0, 13), (250, 13)], fill=0, width=1)
    
    draw.text((5, 15), f"{username}>", font=font12, fill=0)

    if myface and myface[0] == HOT:
        current_quote = "It's getting hot!"
        
    if verus_price is not None:
        draw.text((5, 70), f"Price: ${verus_price:.3f}", font=font15, fill=0)
    else:
        draw.text((5, 70), "Price: N/A", font=font15, fill=0)
    draw.text((5, 88), f"Network: {network_hashrate}/s", font=font12, fill=0)
    draw.text((125, 55), current_quote, font=font12, fill=0)

    draw.text((125, 17), f"{verus_data['balance']} VRSC", font=font15, fill=0)
    draw.text((125, 37), f"{verus_data['hashrate']}/s", font=font12, fill=0)
    
    draw.line([(0, 108), (250, 108)], fill=0, width=1)
    
    label_y = 75  # Starting y position
    value_y = 85  # Starting y position for values
    label_x = 140  # Starting x position for labels
    spacing = 10  # Spacing between labels and values

    mem_label_width = draw.textbbox((0, 0), "mem", font=font10)[2]
    cpu_label_width = draw.textbbox((0, 0), "cpu", font=font10)[2]
    temp_label_width = draw.textbbox((0, 0), "temp", font=font10)[2]

    cpu_label_x = label_x + mem_label_width + spacing
    temp_label_x = cpu_label_x + cpu_label_width + spacing

    mem_value_x = label_x
    cpu_value_x = cpu_label_x
    temp_value_x = temp_label_x

    draw.text((label_x, label_y), "mem", font=font10, fill=0)
    draw.text((cpu_label_x, label_y), "cpu", font=font10, fill=0)
    draw.text((temp_label_x, label_y), "temp", font=font10, fill=0)

    draw.text((mem_value_x, value_y), f"{memory_usage:.1f}%", font=font10, fill=0)
    draw.text((cpu_value_x, value_y), f"{cpu_usage:.0f}%", font=font10, fill=0)
    draw.text((temp_value_x, value_y), f"{cpu_temp}", font=font10, fill=0)

    footer_info(draw, verus_data, font10, screen_width=250)

    if show_graph:
        historical_prices = fetch_historical_prices_with_cache()
        plot_path = plot_prices(historical_prices)
        plot_image = Image.open(plot_path).convert('1')
        image.paste(plot_image, (5, 35)) 

    else:
        if myface:
            draw.text((3, 28), myface[0], font=face32, fill=0)

    image = image.rotate(screen_rotate)
    epd.displayPartial(epd.getbuffer(image))

def main():
    global last_price_fetch_time, last_graph_display_time 
    last_face_display_time = time.time() 
    
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
    show_graph = False

    while True:
        current_time = time.time()
        now = datetime.now()
        
        if current_time - last_cpu_temp_update_time >= 3:
            cpu_temp = get_cpu_temperature()
            cpu_usage, memory_usage = get_cpu_memory_usage()  # Get CPU and memory usage
            last_cpu_temp_update_time = current_time
        
        # Fetch Verus Coin data every 3 minutes
        if current_time - last_fetch_time >= 120:
            try:
                verus_data = get_verus_data(verus_url)
                if verus_data and "balance" in verus_data:
                    current_balance = float(verus_data["balance"])
                    balances.append(current_balance)
                    timestamps.append(current_time)
                    calculate_hourly_average()
                last_fetch_time = current_time
            except Exception as e:
                print(f"Error in fetching Verus data: {e}")

        # Fetch Verus Coin price every 5 minutes
        if current_time - last_price_fetch_time >= 300:
            try:
                verus_price, network_hashrate = fetch_coin_price()
                last_price_fetch_time = current_time
            except Exception as e:
                print(f"Error in fetching coin price: {e}")
                verus_price = manage_price_file()
                network_hashrate = network_hashrate if 'network_hashrate' in locals() else "N/A"

        if not show_graph and (current_time - last_face_display_time >= 60):
            show_graph = True
            last_graph_display_time = current_time

        if show_graph:
            if current_time - last_graph_display_time >= 30:
                show_graph = False
                last_face_display_time = current_time
            else:
                display_verus_data(epd, verus_data, verus_price, network_hashrate, cpu_temp, cpu_usage, memory_usage, now, show_graph=True)
        else:
            display_verus_data(epd, verus_data, verus_price, network_hashrate, cpu_temp, cpu_usage, memory_usage, now, show_graph=False)
            if current_time - last_face_update_time >= 3:
                if verus_data:
                    update_face(verus_data, first_run) 
                    first_run = False  
                last_face_update_time = current_time

            if current_time - last_quote_update_time >= 10:
                current_quote = get_new_quotes() 
                last_quote_update_time = current_time

        time.sleep(3)

if __name__ == "__main__":
    main()
