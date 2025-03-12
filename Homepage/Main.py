import network  # Import network module to handle WiFi connection
import machine  # Import machine module for hardware control
import dht  # Import DHT module to read temperature and humidity
import ssd1306  # Import OLED display driver
import time  # Import time module for delays
import socket  # Import socket module to create a web server
from neopixel import NeoPixel  # Import NeoPixel module for RGB LED control

# Setup WiFi in Station mode
sta = network.WLAN(network.STA_IF)  # Initialize WiFi in station mode
sta.active(True)  # Activate WiFi
sta.connect("Awan-House-445E(1)", "226677899")  # Connect to WiFi network

# Wait until WiFi is connected
while not sta.isconnected():
    pass  # Keep checking until connected

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

# HTML Webpage for controlling the RGB LED
html = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Webserver</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #f9f9f9; padding: 20px; }
        .container { max-width: 350px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1); }
        input { width: 60px; padding: 6px; margin: 5px; text-align: center; }
        button { padding: 10px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <h2>ESP32 RGB LED Control</h2>
        <label>Red:</label> <input type="number" id="red" min="0" max="255" value="0">
        <label>Green:</label> <input type="number" id="green" min="0" max="255" value="0">
        <label>Blue:</label> <input type="number" id="blue" min="0" max="255" value="0"><br>
        <button onclick="setRGB()">Set RGB</button>
        <div class="sensor-data">
            <p>Temperature: <span id="temp">--</span>&deg;C</p>
            <p>Humidity: <span id="humidity">--</span>%</p>
        </div>
    </div>
    <script>
        function setRGB() {
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
        setInterval(updateSensorData, 5000);  // Update sensor data every 5 seconds
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
        
        if "GET /setRGB" in request:
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
        
        else:
            conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + html)  # Serve HTML page

        conn.close()

# Run the web server
web_server()
