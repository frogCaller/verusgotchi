# verusgotchi

<div style="display: flex; gap: 10px;">  
    <img src="images/verusgotchi.jpeg" width="350">
</div>

This project uses a 2.13inch e-ink display with a Raspberry Pi Zero to display verus coin stats using luckpool's API.

# Materials
* [Raspberry pi Zero 2 WH](https://amzn.to/3VO7eu2)<br />
* [Micro SD Cards](https://amzn.to/4erXgWD)<br />
* [2.13inch e-ink](https://amzn.to/3WLFCX2)<br />
* [UPS Hat](https://amzn.to/4ceZp6I)<br />
<br />
(Amazon affiliate links)<br />

## **Installations**

1. **OS install:**
   - Install Raspberry Pi OS Lite (64-bit) on your Raspberry Pi <br />

2. **Enable SPI & I2C:**
   - Open a terminal on your Raspberry Pi.
   - Run `sudo raspi-config`
   - Navigate to Interfacing Options -> SPI -> Enable.
   - Navigate to Interfacing Options -> I2C -> Enable.

3. Clone the repository:
   ```bash
   sudo apt install -y git
   git clone https://github.com/frogCaller/verusgotchi.git
   cd verusgotchi

# Wiring and Setup
1. **Connect 2.13inch e-Ink HAT to Raspberry Pi:**
   - Connect the 2.13inch e-Ink HAT to your Raspberry Pi. <br />
   - Connect the UPS Hat for continuous power supply. This will allow you to move the project anywhere without worrying about power interruptions.

2. **Install System and Python Dependencies:**
   ```bash
   chmod +x setup.sh
   ./setup.sh

# Usage Instructions
1. Edit `main.py` and add your verus wallet:
  - Open main.py in a text editor.
    ```
    nano main.py
    ```
  - Find the line where the wallet address is defined and replace the placeholder with your own Verus wallet address.
  - Add a cool username for your verusgotchi.
    ```
    username = "verusgotchi"
    my_Verus_Wallet = "YOUR_VERUS_WALLET_HERE"
    ```
    
2. Run the script:
   - Run the script: `python3 main.py`


# Troubleshooting
Common Issues:
   - Ensure SPI & I2C are enabled in the Raspberry Pi configuration.
   - Check all connections if the screen does not display anything.
   - Verify all required packages are installed correctly.
   - [More Info](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT_Manual)

# Support the project
If you find this project helpful or interesting, consider supporting me with a small donation in Verus Coin. Your support helps me continue developing and maintaining this project.

**Verus Donation:**

<img src="images/verusDonate.png" width="130">

**Verus Coin Wallet Address:**  
`RQu3rc4EbTB1YVEoeT1WBVrFy69cRausDR`
