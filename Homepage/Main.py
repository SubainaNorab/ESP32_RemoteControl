import network  # Import network module to handle WiFi connection
import machine  # Import machine module for hardware control
import dht  # Import DHT module to read temperature and humidity
import ssd1306  # Import OLED display driver
import time  # Import time module for delays
import socket  # Import socket module to create a web server
from neopixel import NeoPixel  # Import NeoPixel module for RGB LED control
import urequests

# Setup WiFi in Station mode
sta = network.WLAN(network.STA_IF)  # Initialize WiFi in station mode
sta.active(True)  # Activate WiFi
sta.connect("Wifi-79J", "797979jjjj")  # Connect to WiFi network

timeout = 10  # Wait up to 10 seconds
while not sta.isconnected() and timeout > 0:
    print("Connecting to WiFi...")
    time.sleep(1)
    timeout -= 1

# Wait until WiFi is connected
#while not sta.isconnected():
#    pass  # Keep checking until connected

print("Connected! IP:", sta.ifconfig()[0])  # Print assigned IP address

# Define GPIO pins
# Initialize DHT11 sensor on GPIO4
dht_sensor = dht.DHT11(machine.Pin(4))

# Setup OLED Display (Using GPIO9 for SCL & GPIO8 for SDA)
i2c = machine.I2C(scl=machine.Pin(9), sda=machine.Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)  # Set up OLED display with 128x64 resolution

# Setup NeoPixel on GPIO48
pin = machine.Pin(48, machine.Pin.OUT)  # Define GPIO48 as output
neo = NeoPixel(pin, 1)  # Initialize NeoPixel with 1 LED

# Function to set NeoPixel color
def set_color(r, g, b):
    neo[0] = (r, g, b)  # Set RGB values
    neo.write()  # Apply changes
    
def forward_request(path):
    """Forwards requests to the developer mode server running on port 8080."""
    try:
        dev_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dev_server.connect(("127.0.0.1", 8080))  # Connect to the dev server on port 8080
        request = f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n"
        dev_server.send(request.encode())

        response = b""
        while True:
            chunk = dev_server.recv(1024)
            if not chunk:
                break
            response += chunk

        dev_server.close()

        # Extract the response body (remove HTTP headers)
        response_body = response.split(b"\r\n\r\n", 1)[-1].decode()
        return response_body

    except Exception as e:
        print(f"Error forwarding request: {e}")
        return "Error connecting to Developer Mode Server"


def display_text_on_oled(text):
    oled.fill(0)  # Clear display
    oled.text("OLED Display:", 0, 0)
    oled.text(text[:16], 0, 20)  # First 16 characters
    oled.text(text[16:32], 0, 40)  # Next 16 characters if longer
    oled.show()

# HTML Webpage for controlling the RGB LED
html = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Webserver</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        
        body {
            font-family: 'Poppins', sans-serif;
            text-align: center;
            background: url('https://wallpapercave.com/wp/wp2563382.jpg') no-repeat center center fixed;
            background-size: cover;
            color: #ffffff;
            padding: 20px;
        }
        .container {
            max-width: 400px;
            margin: auto;
            background: rgba(0, 0, 0, 0.85);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 4px 4px 15px rgba(0, 0, 0, 0.4);
        }
        h2 {
            color: #ffcc00;
        }
        input[type="range"] {
            width: 100%;
            margin: 10px 0;
            accent-color: #ffcc00;
        }
        input[type="text"] {
            width: 90%;
            padding: 10px;
            margin-top: 10px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
        }
        button {
            padding: 12px;
            background: #ff5733;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
            transition: 0.3s;
        }
        button:hover {
            background: #ffcc00;
            transform: scale(1.05);
        }
        .sensor-data {
            margin-top: 15px;
            font-size: 18px;
            background: rgba(255, 255, 255, 0.2);
            padding: 10px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class='container'>
        <h2>ESP32 RGB LED Control</h2>
        <label>Red:</label>
        <input type='range' id='red' min='0' max='255' value='0' oninput='sendRGB()'>
        <br>
        <label>Green:</label>
        <input type='range' id='green' min='0' max='255' value='0' oninput='sendRGB()'>
        <br>
        <label>Blue:</label>
        <input type='range' id='blue' min='0' max='255' value='0' oninput='sendRGB()'>
        <br>
        <div class="container">
            <h2>ESP32 OLED Display</h2>
            <input type="text" id="oledText" placeholder="Enter text">
            <button onclick="sendText()">Display on OLED</button>
        </div>
        <br>
        <div class='sensor-data'>
            <p>Temperature: <span id='temp'>--</span>°C</p>
            <p>Humidity: <span id='humidity'>--</span>%</p>
        </div>
        <br>
        <button onclick='toggleDevMode()'>Developer Mode</button>
    </div>
    <script>
        function sendRGB() {
            let r = document.getElementById('red').value;
            let g = document.getElementById('green').value;
            let b = document.getElementById('blue').value;
            fetch(`/setRGB?r=${r}&g=${g}&b=${b}`);
        }
        function updateSensorData() {
            fetch('/sensorData')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('temp').innerText = data.temperature;
                    document.getElementById('humidity').innerText = data.humidity;
                });
        }
        setInterval(updateSensorData, 5000);
        function sendText() {
            let text = document.getElementById('oledText').value;
            fetch(`/displayText?text=${encodeURIComponent(text)}`);
        }
        function toggleDevMode() {
            window.location.href = '/index.html';
        }
    </script>
</body>
</html>
"""

# Start a simple web server using sockets
def web_server():
    addr = ('', 80)  # Listen on all available interfaces, port 80
    s = socket.socket()
    s.bind(addr)
    s.listen(5)  # Allow up to 5 connections
    
    print("Server running...")
    
    while True:
        conn, addr = s.accept()  # Accept incoming connection
        request = conn.recv(1024).decode()  # Read request data
        
        if "GET / " in request or "GET /home.html" in request:
            with open("home.html", "r") as file:
                home_html = file.read()
            conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + home_html)

        
        elif "GET /setRGB" in request:
            try:
                params = request.split(" ")[1].split("?")[1]  # Extract parameters from URL
                r, g, b = [int(param.split("=")[1]) for param in params.split("&")]  # Parse RGB values
                set_color(r, g, b)  # Update NeoPixel color

                # Update OLED display with RGB values
                oled.fill(0)
                oled.text(f"RGB: {r},{g},{b}", 0, 10)
                oled.show()

                conn.send("HTTP/1.1 200 OK\nContent-Type: text/plain\n\nRGB Updated")
            except:
                conn.send("HTTP/1.1 400 Bad Request\n\nInvalid Input")

        elif "GET /sensorData" in request:
            dht_sensor.measure()  # Read DHT11 sensor
            temp = dht_sensor.temperature()
            humidity = dht_sensor.humidity()
            
            # Update OLED display with temperature and humidity
            oled.fill(0)
            oled.text(f"Temp: {temp}C", 0, 10)
            oled.text(f"Humidity: {humidity}%", 0, 30)
            oled.show()

            conn.send(f"HTTP/1.1 200 OK\nContent-Type: application/json\n\n{{\"temperature\": {temp}, \"humidity\": {humidity}}}")
            
        elif "GET /index.html" in request:
            with open("../index.html", "r") as file:  # Adjust path if necessary
                index_html = file.read()
            conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + index_html)

            
        elif "GET /displayText" in request:
            try:
                params = request.split(" ")[1].split("?")[1]  # Extract parameters
                text = params.split("=")[1].replace("+", " ")  # Get text value
                display_text_on_oled(text)  # Show text on OLED
                conn.send("HTTP/1.1 200 OK\nContent-Type: text/plain\n\nText Displayed")
            except:
                conn.send("HTTP/1.1 400 Bad Request\n\nInvalid Input")
                
        elif "GET /files" in request or "GET /system" in request or "POST /encrypt" in request or "POST /decrypt" in request:
            response = forward_request(request.split(" ")[1])  # Extract request path
            content_type = "text/plain"
        
        else:
            #conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + html)  # Serve HTML page
            response = "404 Not Found"
            content_type = "text/plain"

        conn.close()

# Run the web server
web_server()