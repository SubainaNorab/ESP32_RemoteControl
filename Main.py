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

# Read HTML File
def read_html():
    with open("index.html", "r") as file:
        return file.read()

# List Files
def list_files():
    return "\n".join(os.listdir())

# Encrypt Text
def encrypt_text(data):
    key = 42
    return ubinascii.hexlify(bytes([b ^ key for b in data.encode()])).decode()

# Start Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 80))
server.listen(5)

print("🌐 Server started. Waiting for connections...")

while True:
    conn, addr = server.accept()
    request = conn.recv(1024).decode()
    print(f"🔹 Received request: {request}")  # Debugging line

    if "GET / " in request:
        response = read_html()
        content_type = "text/html"
    
    elif "GET /files" in request:
        response = list_files()
        content_type = "text/plain"
    
    elif "POST /encrypt" in request:
        content = request.split("\r\n\r\n")[-1]
        response = encrypt_text(content)
        content_type = "text/plain"
    
    else:
        response = "404 Not Found"
        content_type = "text/plain"
    
    conn.send(f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(response)}\r\n\r\n{response}".encode())
    conn.close()
    gc.collect()
