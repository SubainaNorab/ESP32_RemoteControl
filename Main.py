import network
import socket
import os
import ubinascii
import gc

# Wi-Fi Credentials
SSID = "Sbain"
PASSWORD = "cant7301"

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    pass

print(f"✅ Connected to WiFi! IP Address: {wlan.ifconfig()[0]}")

# Function to read HTML file
def read_html():
    with open("index.html", "r") as file:
        return file.read()

# Function to list files
def list_files():
    return str(os.listdir())

# Function to encrypt text
def encrypt_text(data):
    key = 42  # XOR key
    encrypted = ubinascii.hexlify(bytes([b ^ key for b in data.encode()])).decode()
    return encrypted

# Start Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 80))
server.listen(5)

print("🌐 Server started. Waiting for connections...")

while True:
    conn, addr = server.accept()
    request = conn.recv(1024).decode()
    
    # Serve Web Page
    if "GET / " in request:
        response = read_html()
        content_type = "text/html"
    
    # File Listing
    elif "GET /files" in request:
        response = list_files()
        content_type = "text/plain"
    
    # Encrypt Text
    elif "POST /encrypt" in request:
        content = request.split("\r\n\r\n")[-1]
        response = encrypt_text(content)
        content_type = "text/plain"

    else:
        response = "404 Not Found"
        content_type = "text/plain"
    
    # Send Response
    conn.send(f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(response)}\r\n\r\n{response}".encode())
    conn.close()
    gc.collect()  # Free memory

