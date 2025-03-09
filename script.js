async function fetchFiles() {
    const response = await fetch('/files');
    const data = await response.json();
    document.getElementById('files').textContent = JSON.stringify(data, null, 2);
}

async function fetchSystemInfo() {
    const response = await fetch('/system');
    const data = await response.json();
    document.getElementById('system').textContent = `Free RAM: ${data.heap_free} bytes\nCPU Usage: ${data.cpu_usage}`;
}

async function fetchWiFi() {
    const response = await fetch('/wifi');
    const data = await response.json();
    document.getElementById('wifi').textContent = `IP Address: ${data.ip}`;
}

async function encryptText() {
    const text = document.getElementById('inputText').value;
    if (!text) {
        alert("Please enter text to encrypt.");
        return;
    }

    const response = await fetch('/encrypt', {
        method: 'POST',
        body: text,
    });

    const data = await response.json();
    document.getElementById('encrypted').textContent = `Encrypted: ${data.encrypted}`;
}

