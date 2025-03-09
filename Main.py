import network
import machine
import gc
import time
import socket
import ubinascii
from machine import Pin, I2C
import ssd1306

# Wi-Fi Credentials
ID_STA = "Sbain"
password_STA = "cant7301"

# Connect to Wi-Fi (STA Mode)
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(ID_STA, password_STA)

# Wait for STA Connection
for _ in range(10):
    if sta.isconnected():
        break
    time.sleep(1)

ip_address = sta.ifconfig()[0] if sta.isconnected() else "Not Connected"
print("STA Mode IP:", ip_address)

# OLED Setup
i2c = I2C(0, scl=Pin(9), sda=Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# XOR Encryption Function
def xor_encrypt_decrypt(text, key=42):  # 42 is a simple XOR key
    return "".join(chr(ord(c) ^ key) for c in text)

# Get ESP32 System Info
def get_esp_info():
    gc.collect()
    total_ram = gc.mem_alloc() + gc.mem_free()
    free_ram = gc.mem_free()
    used_ram = total_ram - free_ram
    cpu_freq = machine.freq() // 1000000
    return f"Total RAM: {total_ram} | Used: {used_ram} | Free: {free_ram} | CPU: {cpu_freq} MHz"

# Start Web Server
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(('', 80))
soc.listen(5)
print("Server started. Waiting for connections...")

while True:
    conn, addr = soc.accept()
    request = conn.recv(1024).decode()
    print("Request:", request)

    # Serve HTML & JS files
    if "GET / " in request:
        with open("index.html", "r") as f:
            response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + f.read()

    elif "GET /script.js" in request:
        with open("script.js", "r") as f:
            response = "HTTP/1.1 200 OK\nContent-Type: application/javascript\n\n" + f.read()

    # Handle Encrypted Voice Command
    elif "GET /command?" in request:
        try:
            params = request.split("GET /command?cmd=")[1].split(" ")[0]
            command = params.replace("+", " ")

            # Decrypt before displaying on OLED
            decrypted_command = xor_encrypt_decrypt(command)
            print("Decrypted Command:", decrypted_command)

            oled.fill(0)
            oled.text("Enc:", 0, 0)
            oled.text(command[:16], 0, 20)  # Show encrypted text
            oled.text("Dec:", 0, 40)
            oled.text(decrypted_command[:16], 0, 50)  # Show decrypted text
            oled.show()

            response = "HTTP/1.1 200 OK\nContent-Type: text/plain\n\nOK"
        except:
            response = "HTTP/1.1 400 Bad Request\nContent-Type: text/plain\n\nError processing command"

    # Handle ESP Info Request
    elif "GET /system" in request:
        system_info = get_esp_info()
        response = "HTTP/1.1 200 OK\nContent-Type: text/plain\n\n" + system_info

    else:
        response = "HTTP/1.1 404 Not Found\nContent-Type: text/html\n\nPage Not Found"

    conn.send(response)
    conn.close()
