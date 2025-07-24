from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import time

app = Flask(__name__)
CORS(app)  # 允許跨來源請求

DB_NAME = "seismic_data.db"

# 初始化資料庫
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seismic_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station TEXT,
            x REAL,
            y REAL,
            z REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# API 狀態檢查
@app.route('/')
def index():
    return jsonify({"message": "Seismic API is running!"})

# 統一路由：上傳與取得地震資料
@app.route('/api/seismic', methods=['GET', 'POST'])
def seismic_data():
    if request.method == 'POST':
        try:
            data = request.get_json()
            station = data.get('station')
            x = data.get('x')
            y = data.get('y')
            z = data.get('z')
            timestamp = data.get('timestamp', time.strftime("%Y-%m-%d %H:%M:%S"))

            if not station or x is None or y is None or z is None:
                return jsonify({"status": "error", "message": "Missing data fields"}), 400

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO seismic_data (station, x, y, z, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (station, x, y, z, timestamp))
            conn.commit()
            conn.close()

            return jsonify({"status": "success", "message": "Data stored"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    elif request.method == 'GET':
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT station, x, y, z, timestamp FROM seismic_data ORDER BY id DESC LIMIT 100')
        rows = cursor.fetchall()
        conn.close()

        data = [{
            "station": row[0],
            "x": row[1],
            "y": row[2],
            "z": row[3],
            "timestamp": row[4]
        } for row in rows]

        return jsonify(data)

# 取得特定測站資料
@app.route('/api/seismic/<station>', methods=['GET'])
def get_station_data(station):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT x, y, z, timestamp FROM seismic_data WHERE station = ? ORDER BY id DESC LIMIT 100', (station,))
    rows = cursor.fetchall()
    conn.close()

    data = [{
        "x": row[0],
        "y": row[1],
        "z": row[2],
        "timestamp": row[3]
    } for row in rows]

    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
