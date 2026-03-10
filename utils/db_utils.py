import sqlite3

def save_alert(timestamp, image_path, confidence):
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO alerts (timestamp, image_path, confidence) VALUES (?, ?, ?)', (timestamp, image_path, confidence))
    conn.commit()
    conn.close()

def get_alerts():
    conn = sqlite3.connect('database.db')
    alerts = conn.execute('SELECT * FROM alerts ORDER BY timestamp DESC').fetchall()
    conn.close()
    return alerts