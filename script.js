function fetchFiles() {
    fetch("/files")
        .then(response => response.json())
        .then(data => {
            document.getElementById("files").innerText = JSON.stringify(data, null, 2);
        });
}

function fetchSystemInfo() {
    fetch("/system")
        .then(response => response.json())
        .then(data => {
            document.getElementById("system").innerText = `RAM: ${data.free_ram} bytes, CPU: ${data.cpu_freq} Hz`;
        });
}

function fetchWiFi() {
    fetch("/wifi")
        .then(response => response.json())
        .then(data => {
            document.getElementById("wifi").innerText = `Signal: ${data.rssi} dBm, Connected: ${data.is_connected}`;
        });
}

function encryptText() {
    let text = document.getElementById("inputText").value;
    fetch("/encrypt", { method: "POST", body: text })
        .then(response => response.text())
        .then(data => {
            document.getElementById("encrypted").innerText = `Encrypted: ${data}`;
        });
}