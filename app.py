from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "mechmemory.db")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT NOT NULL,
                temperature REAL NOT NULL,
                vibration REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT NOT NULL,
                symptom TEXT NOT NULL,
                action TEXT NOT NULL,
                outcome TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/latest")
def latest():
    with db() as conn:
        row = conn.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1").fetchone()
    if row is None:
        return jsonify({"available": False, "message": "No ESP32 readings received yet"})
    return jsonify({"available": True, **dict(row)})

@app.get("/api/readings")
def get_readings():
    with db() as conn:
        rows = conn.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 50").fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/readings")
def post_reading():
    data = request.get_json(silent=True) or {}
    try:
        machine_id = str(data.get("machine_id", "MCH-001"))[:40]
        temperature = float(data["temperature"])
        vibration = float(data["vibration"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"ok": False, "error": "Expected machine_id, temperature, vibration"}), 400

    # Server-side classification keeps the dashboard and stored status consistent.
    status = "ANOMALY" if temperature > 70.0 or vibration > 7.0 else "NORMAL"
    created_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    with db() as conn:
        cur = conn.execute(
            "INSERT INTO readings(machine_id, temperature, vibration, status, created_at) VALUES(?,?,?,?,?)",
            (machine_id, temperature, vibration, status, created_at)
        )
        reading_id = cur.lastrowid

    print(f"[{created_at}] {machine_id}: T={temperature:.1f} C, V={vibration:.2f}, {status}", flush=True)
    return jsonify({"ok": True, "id": reading_id, "machine_id": machine_id,
                    "temperature": temperature, "vibration": vibration,
                    "status": status, "created_at": created_at}), 201

@app.post("/api/maintenance")
def add_maintenance():
    data = request.get_json(silent=True) or {}
    required = ("machine_id", "symptom", "action", "outcome")
    if any(not data.get(k) for k in required):
        return jsonify({"ok": False, "error": "machine_id, symptom, action and outcome are required"}), 400
    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    with db() as conn:
        conn.execute("INSERT INTO maintenance(machine_id,symptom,action,outcome,created_at) VALUES(?,?,?,?,?)",
                     tuple(str(data[k])[:500] for k in required) + (created_at,))
    return jsonify({"ok": True}), 201

@app.get("/api/maintenance")
def get_maintenance():
    with db() as conn:
        rows = conn.execute("SELECT * FROM maintenance ORDER BY id DESC LIMIT 100").fetchall()
    return jsonify([dict(r) for r in rows])

# Create the database schema when the app starts, including under Gunicorn.
init_db()

if __name__ == "__main__":
    # Local development server. Render uses the Gunicorn start command.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
