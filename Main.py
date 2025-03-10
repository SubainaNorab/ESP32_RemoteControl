import network
import socket
import os
import ubinascii
import gc
import machine
import ssd1306

# Wi-Fi Credentials
SSID = "Sbain"
PASSWORD = "cant7301"

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    pass

print(f"Connected to WiFi! IP Address: {wlan.ifconfig()[0]}")

# Setup Access Point Mode (Optional)
AP_SSID = "SSS"
AP_PASSWORD = "12345678"
AP_AUTH_MODE = network.AUTH_WPA2_PSK

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=AP_AUTH_MODE)
print("Access Point Active")
print("AP IP Address:", ap.ifconfig()[0])

# Initialize OLED Display
i2c = machine.I2C(scl=machine.Pin(9), sda=machine.Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Store last encrypted text
last_encrypted = ""

# Read HTML File
def read_html():
    try:
        with open("index.html", "r") as file:
            return file.read()
    except:
        return "<h1>index.html Not Found</h1>"

# List Files in ESP32
def list_files():
    return "\n".join(os.listdir())

# Serve Image File in Chunks
def serve_file(filename, conn):
    try:
        with open(filename, "rb") as file:
            conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nConnection: close\r\n\r\n")
            while True:
                chunk = file.read(1024)  # Send in 1024-byte chunks
                if not chunk:
                    break
                conn.sendall(chunk)
    except:
        conn.send(b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nFile not found")

# Encrypt Text
def encrypt_text(data):
    global last_encrypted
    key = 42
    encrypted = ubinascii.hexlify(bytes([b ^ key for b in data.encode()])).decode()
    last_encrypted = encrypted  # Store encrypted text
    display_encryption(encrypted)  # Show on OLED
    return encrypted

# Decrypt Text
def decrypt_text(data):
    key = 42
    decrypted = bytes([b ^ key for b in ubinascii.unhexlify(data)]).decode()
    display_encryption(last_encrypted, decrypted)  # Show both encrypted & decrypted on OLED
    return decrypted

# Display Encrypted & Decrypted Text on OLED
def display_encryption(enc_text, dec_text=None):
    oled.fill(0)  # Clear display
    oled.text("Enc:", 0, 0)
    oled.text(enc_text[:16], 0, 10)
    oled.text(enc_text[16:], 0, 20)

    if dec_text:
        oled.text("Dec:", 0, 40)
        oled.text(dec_text[:16], 0, 50)
        oled.text(dec_text[16:], 0, 60)

    oled.show()

# Get System Monitoring Info
def get_system_info():
    total_ram = gc.mem_alloc() + gc.mem_free()
    used_ram = gc.mem_alloc()
    free_ram = gc.mem_free()
    return f"Total RAM: {total_ram} bytes\nUsed RAM: {used_ram} bytes\nFree RAM: {free_ram} bytes"

# Start Web Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 80))
server.listen(5)

print("Server started. Waiting for connections...")

while True:
    conn, addr = server.accept()
    request = conn.recv(1024).decode()
    print(f"Received request: {request}")

    response = "404 Not Found"
    content_type = "text/plain"

    if "GET / " in request or "GET /index.html" in request:
        response = read_html()
        content_type = "text/html"

    elif "GET /light.jpg" in request:
        serve_file("light.jpg", conn)
        conn.close()
        continue

    elif "GET /files" in request:
        response = list_files()
        content_type = "text/plain"

    elif "GET /system" in request:
        response = get_system_info()
        content_type = "text/plain"

    elif "POST /encrypt" in request:
        content = request.split("\r\n\r\n")[-1]
        response = encrypt_text(content)  # Encrypt and show on OLED
        content_type = "text/plain"

    elif "POST /decrypt" in request:
        content = request.split("\r\n\r\n")[-1]
        response = decrypt_text(content)  # Decrypt and show on OLED
        content_type = "text/plain"

    # Send HTTP Response
    conn.send(f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(response)}\r\n\r\n".encode())
    conn.sendall(response.encode() if isinstance(response, str) else response)
    conn.close()
    gc.collect()

