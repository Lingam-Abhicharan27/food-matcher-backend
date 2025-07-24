from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from utils import init_db, get_db_connection

app = Flask(__name__)
CORS(app)
init_db()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = generate_password_hash(data['password'])

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return jsonify({"status": "success", "message": "User registered successfully."})
    except sqlite3.IntegrityError:
        return jsonify({"status": "fail", "message": "Username already exists."})
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "success", "message": "Login successful"})
    else:
        return jsonify({"status": "fail", "message": "Invalid credentials"}), 401


@app.route('/donate', methods=['POST'])
def donate():
    from haversine import haversine

    data = request.json
    donor_location = (data["latitude"], data["longitude"])
    food_type = data["food_type"].lower()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ngos")
    ngos = cursor.fetchall()
    conn.close()

    matched_ngos = []
    for ngo in ngos:
        ngo_location = (ngo['latitude'], ngo['longitude'])
        distance = haversine(donor_location, ngo_location)
        if distance <= ngo['radius_km'] and food_type in ngo['accepted_food'].split(','):
            matched_ngos.append({
                "ngo_name": ngo['name'],
                "distance_km": round(distance, 2)
            })

    if matched_ngos:
        matched_ngos.sort(key=lambda x: x['distance_km'])
        return jsonify({"status": "success", "matched_ngos": matched_ngos})
    else:
        return jsonify({"status": "fail", "message": "No matching NGO found nearby."})

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
