import sqlite3

def init_db():
    conn = sqlite3.connect("alerts.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS alerts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            image TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_alert(time, image):
    conn = sqlite3.connect("alerts.db")
    c = conn.cursor()
    c.execute("INSERT INTO alerts(time,image) VALUES(?,?)",(time,image))
    conn.commit()
    conn.close()
