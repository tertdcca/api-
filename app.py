from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'seismic.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS seismic_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            lat REAL,
            lon REAL,
            ax REAL,
            ay REAL,
            az REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/seismic', methods=['POST'])
def receive_data():
    data = request.get_json()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO seismic_data (device_id, lat, lon, ax, ay, az, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('device_id'),
        data.get('lat'),
        data.get('lon'),
        data.get('ax'),
        data.get('ay'),
        data.get('az'),
        data.get('timestamp', datetime.utcnow().isoformat())
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201

@app.route('/api/seismic/all', methods=['GET'])
def get_all_data():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM seismic_data')
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
