import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS ngos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        accepted_food TEXT NOT NULL,
        radius_km REAL NOT NULL
    )''')

    # Insert sample NGOs only if table is empty
    cursor.execute('SELECT COUNT(*) FROM ngos')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''INSERT INTO ngos (name, latitude, longitude, accepted_food, radius_km) VALUES (?, ?, ?, ?, ?)''', [
            ("Helping Hands NGO", 17.385044, 78.486671, "rice,bread,fruits", 10),
            ("Hope For All", 17.4239, 78.4867, "vegetables,bread", 5)
        ])
    
    conn.commit()
    conn.close()