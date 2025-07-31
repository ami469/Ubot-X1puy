from flask import Flask
import os
from threading import Thread

app = Flask(__name__)

# Halaman utama panel
@app.route("/")
def home():
    return """
    <h1>✅ UBot Panel Aktif</h1>
    <ul>
        <li><a href='/restart'>🔄 Restart Bot</a></li>
        <li><a href='/update'>⬆️ Update Bot (git pull)</a></li>
        <li><a href='/ping'>📶 Ping</a></li>
    </ul>
    """

# Restart bot
@app.route("/restart")
def restart():
    os.system("pkill -f main.py && nohup python3 main.py &")
    return "✅ Bot berhasil direstart!"

# Git pull update
@app.route("/update")
def update():
    os.system("git pull origin main")
    return "✅ Bot berhasil diupdate dari GitHub."

# Cek status
@app.route("/ping")
def ping():
    return "✅ Bot aktif & panel hidup!"

# Fungsi keep_alive() ala Replit
def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Kalau ingin dijalankan langsung dari panel.py
if __name__ == "__main__":
    run()