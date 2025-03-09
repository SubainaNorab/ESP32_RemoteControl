import network
import uos
import machine
import socket
import gc
import esp32
import time
import json

# Enable garbage collection
gc.collect()

# Wi-Fi Configuration
SSID = "Sbain"
PASSWORD = "cant7301"

# Connect ESP32 to Wi-Fi
sta = network.WLAN(network.STA_IF)
sta.active(True)

if not sta.isconnected():
    print("Connecting to WiFi", end="")
    sta.connect(SSID, PASSWORD)
    
    for _ in range(15):  # More attempts for better stability
        if sta.isconnected():
            break
        print(".", end="")  # Show progress
        time.sleep(1)

if sta.isconnected():
    ip_address = sta.ifconfig()[0]
    print(f"\n✅ Connected to WiFi! IP Address: {ip_address}")
else:
    print("\n❌ Failed to connect. Check credentials or signal strength.")
    machine.reset()  # Restart ESP32 if WiFi fails


# Encryption function (simple XOR)
def encrypt(text, key=5):
    return ''.join(chr(ord(c) ^ key) for c in text)

# Function to list files in SPIFFS
def list_files():
    files = uos.listdir()
    categorized_files = {"html": [], "js": [], "py": []}
    for file in files:
        if file.endswith(".html"):
            categorized_files["html"].append(file)
        elif file.endswith(".js"):
            categorized_files["js"].append(file)
        elif file.endswith(".py"):
            categorized_files["py"].append(file)
    return json.dumps(categorized_files)

# Function to read a file
def read_file(filename):
    try:
        with open(filename, "r") as f:
            return f.read()
    except:
        return "Error: File not found."

# Function to check RAM and CPU usage
def get_system_info():
    return json.dumps({
        "free_ram": gc.mem_free(),
        "cpu_freq": machine.freq()
    })

# Function to test Wi-Fi signal
def get_wifi_signal():
    return json.dumps({
        "rssi": sta.status("rssi"),
        "is_connected": sta.isconnected()
    })

# Function to serve static files (HTML, JS, CSS)
def serve_static_file(filename):
    content = read_file(filename)
    if filename.endswith(".html"):
        content_type = "text/html"
    elif filename.endswith(".js"):
        content_type = "application/javascript"
    elif filename.endswith(".css"):
        content_type = "text/css"
    else:
        content_type = "text/plain"

    return f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n{content}"


# Start Web Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reusing the address
server.bind(('', 80))  # Use port 80
server.listen(5)

print("🌐 Server started. Waiting for connections...")

while True:
    try:
        conn, addr = server.accept()
        print(f"📡 Connection from {addr}")
        request = conn.recv(1024).decode()
        
        # Handle different requests
        if "GET /files" in request:
            response = list_files()
        elif "GET /read?file=" in request:
            filename = request.split("GET /read?file=")[1].split(" ")[0]
            response = read_file(filename)
        elif "GET /system" in request:
            response = get_system_info()
        elif "GET /wifi" in request:
            response = get_wifi_signal()
        elif "POST /encrypt" in request:
            text = request.split("\r\n\r\n")[-1]
            response = encrypt(text)
        elif "GET /script.js" in request:
            response = serve_static_file("script.js")
        elif "GET /" in request:  # Serve index.html
            response = serve_static_file("index.html")
        else:
            response = "Invalid Request"

        conn.send("HTTP/1.1 200 OK\nContent-Type: application/json\n\n" + response)
        conn.close()
    
    except Exception as e:
        print(f"❌ Error: {e}")

