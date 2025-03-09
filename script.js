// XOR Encryption for Browser
function xorEncrypt(text, key) {
    return text.split('').map(c => String.fromCharCode(c.charCodeAt(0) ^ key)).join('');
}

function sendCommand() {
    var cmd = document.getElementById("commandInput").value;
    var encryptedCmd = xorEncrypt(cmd, 42);  // Encrypt before sending
    document.getElementById("output").innerText = encryptedCmd;
    
    fetch('/command?cmd=' + encodeURIComponent(encryptedCmd))
        .then(() => { 
            document.getElementById("decryptedOutput").innerText = cmd;
        });
}
function updateSystemInfo() {
    fetch('/system')
        .then(response => response.text())
        .then(data => { document.getElementById("systemInfo").innerText = data; });
}
setInterval(updateSystemInfo, 5000);