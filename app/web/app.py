
from flask import Flask, jsonify, render_template
import os, shutil, socket, subprocess

app = Flask(__name__)
SERVICES = ["tomcat10", "docker", "k3s", "postgresql"]

def rate(value, warn, crit, higher_is_bad=True):
    if higher_is_bad:
        return "crit" if value >= crit else "warn" if value >= warn else "ok"
    return "crit" if value <= crit else "warn" if value <= warn else "ok"

def meminfo():
    data = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, value = line.split(":")
            data[key] = int(value.split()[0])
    return data

def service_state(name):
    result = subprocess.run(["systemctl", "is-active", name], capture_output=True, text=True)
    return result.stdout.strip()

@app.route("/api/health")
def health():
    cores = os.cpu_count()
    load1 = os.getloadavg()[0]
    mem = meminfo()
    mem_pct = mem["MemAvailable"] * 100 / mem["MemTotal"]
    disk = shutil.disk_usage("/")
    disk_pct = disk.used * 100 / disk.total
    with open("/proc/uptime") as f:
        uptime_h = float(f.read().split()[0]) / 3600
    return jsonify({
        "host": socket.gethostname(),
        "uptime_hours": round(uptime_h, 1),
        "cpu": {"load": round(load1, 2), "cores": cores,
                "status": rate(load1 / cores, 0.7, 1.0)},
        "memory": {"available_mb": mem["MemAvailable"] // 1024, "total_mb": mem["MemTotal"] // 1024,
                   "available_pct": round(mem_pct),
                   "status": rate(mem_pct, 20, 10, higher_is_bad=False)},
        "disk": {"used_pct": round(disk_pct), "free_gb": disk.free // 2**30,
                 "status": rate(disk_pct, 80, 90)},
        "services": {s: service_state(s) for s in SERVICES},
    })

@app.route("/")
def home():
    return render_template("index.html")
