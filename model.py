import sqlite3

DATABASE = 'sleep_tracker.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        password TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS sleep_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        date TEXT,
                        sleep_time TEXT,
                        wakeup_time TEXT,
                        duration TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')

if __name__ == '__main__':
    init_db()
