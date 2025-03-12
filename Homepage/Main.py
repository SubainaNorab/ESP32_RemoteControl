import network
import machine
import dht
import ssd1306
import time
import socket
from neopixel import NeoPixel

# Setup WiFi in Station mode
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("Awan-House-445E(1)", "226677899")

while not sta.isconnected():
    pass  # Wait for connection

print("Connected! IP:", sta.ifconfig()[0])

# Define GPIO pins
dht_sensor = dht.DHT11(machine.Pin(4))  # DHT11 sensor on GPIO4

# Setup OLED Display (Using GPIO9 for SCL & GPIO8 for SDA)
i2c = machine.I2C(scl=machine.Pin(9), sda=machine.Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Setup NeoPixel on GPIO48
pin = machine.Pin(48, machine.Pin.OUT)
neo = NeoPixel(pin, 1)  # 1 NeoPixel LED

# Function to set NeoPixel color
def set_color(r, g, b):
    neo[0] = (r, g, b)
    neo.write()

# HTML Webpage with Improved CSS
html = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Webserver</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background: linear-gradient(135deg, #f3f4f6, #dfe3e8);
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 400px;
            margin: auto;
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        }
        h2 {
            color: #333;
            margin-bottom: 15px;
        }
        label {
            font-size: 16px;
            font-weight: bold;
            margin-right: 5px;
        }
        input {
            width: 65px;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 6px;
            text-align: center;
            font-size: 16px;
            margin: 5px;
            transition: border-color 0.3s;
        }
        input:focus {
            border-color: #4CAF50;
            outline: none;
        }
        button {
            padding: 12px 18px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 18px;
            margin-top: 10px;
            transition: background 0.3s, transform 0.1s;
        }
        button:hover {
            background: #45a049;
        }
        button:active {
            transform: scale(0.98);
        }
        .sensor-data {
            margin-top: 20px;
            font-size: 16px;
            color: #555;
        }
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
            <p>Temperature: <span id="temp">--</span>°C</p>
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
        setInterval(updateSensorData, 5000);
    </script>
</body>
</html>
"""

# Start a simple web server using sockets
def web_server():
    addr = ('', 80)
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    
    print("Server running...")
    
    while True:
        conn, addr = s.accept()
        request = conn.recv(1024).decode()
        
        if "GET /setRGB" in request:
            try:
                params = request.split(" ")[1].split("?")[1]
                r, g, b = [int(param.split("=")[1]) for param in params.split("&")]
                set_color(r, g, b)  # Update NeoPixel color

                # Update OLED
                oled.fill(0)
                oled.text(f"RGB: {r},{g},{b}", 0, 10)
                oled.show()

                conn.send("HTTP/1.1 200 OK\nContent-Type: text/plain\n\nRGB Updated")
            except:
                conn.send("HTTP/1.1 400 Bad Request\n\nInvalid Input")

        elif "GET /sensorData" in request:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            humidity = dht_sensor.humidity()
            
            oled.fill(0)
            oled.text(f"Temp: {temp}C", 0, 10)
            oled.text(f"Humidity: {humidity}%", 0, 30)
            oled.show()

            conn.send(f"HTTP/1.1 200 OK\nContent-Type: application/json\n\n{{\"temperature\": {temp}, \"humidity\": {humidity}}}")
        
        else:
            conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + html)

        conn.close()

# Run the web server
web_server()
