
from flask import Flask
import os, shutil, socket

app = Flask(__name__)

def meminfo():
    data = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, value = line.split(":")
            data[key] = int(value.split()[0])   # values are in kB
    return data

@app.route("/")
def home():
    load1, load5, load15 = os.getloadavg()
    mem = meminfo()
    disk = shutil.disk_usage("/")
    with open("/proc/uptime") as f:
        up_hours = float(f.read().split()[0]) / 3600
    return f"""
    <h1>Ultron</h1>
    <p>Watching <b>{socket.gethostname()}</b></p>
    <ul>
      <li>Uptime: {up_hours:.1f} hours</li>
      <li>Load (1/5/15 min): {load1:.2f} / {load5:.2f} / {load15:.2f} on {os.cpu_count()} cores</li>
      <li>Memory available: {mem['MemAvailable']//1024} MB of {mem['MemTotal']//1024} MB</li>
      <li>Disk /: {disk.used*100//disk.total}% used ({disk.free//2**30} GB free)</li>
    </ul>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
