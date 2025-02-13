from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Add a secret key for session management

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

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                return redirect(url_for('logs'))
            else:
                return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        with sqlite3.connect(DATABASE) as conn:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        date = request.form.get('date')
        sleep_time = request.form.get('sleep_time')
        wakeup_time = request.form.get('wakeup_time')

        sleep_dt = datetime.strptime(sleep_time, '%H:%M')
        wakeup_dt = datetime.strptime(wakeup_time, '%H:%M')

        if wakeup_dt < sleep_dt:
            wakeup_dt += timedelta(days=1)

        duration = wakeup_dt - sleep_dt

        with sqlite3.connect(DATABASE) as conn:
            conn.execute('INSERT INTO sleep_entries (user_id, date, sleep_time, wakeup_time, duration) VALUES (?, ?, ?, ?, ?)',
                         (session['user_id'], date, sleep_time, wakeup_time, str(duration)))

        return redirect(url_for('logs'))

    return render_template('new_entry.html')

@app.route('/logs')
def logs():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('SELECT * FROM sleep_entries WHERE user_id = ? ORDER BY date DESC LIMIT 7', (session['user_id'],))
        logs = cursor.fetchall()
    return render_template('logs.html', logs=logs)

@app.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        date = request.form.get('date')
        sleep_time = request.form.get('sleep_time')
        wakeup_time = request.form.get('wakeup_time')

        sleep_dt = datetime.strptime(sleep_time, '%H:%M')
        wakeup_dt = datetime.strptime(wakeup_time, '%H:%M')

        if wakeup_dt < sleep_dt:
            wakeup_dt += timedelta(days=1)

        duration = wakeup_dt - sleep_dt

        with sqlite3.connect(DATABASE) as conn:
            conn.execute('UPDATE sleep_entries SET date = ?, sleep_time = ?, wakeup_time = ?, duration = ? WHERE id = ?',
                         (date, sleep_time, wakeup_time, str(duration), entry_id))

        return redirect(url_for('logs'))

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('SELECT * FROM sleep_entries WHERE id = ?', (entry_id,))
        entry = cursor.fetchone()
    return render_template('edit_entry.html', entry=entry)

@app.route('/delete_entry/<int:entry_id>')
def delete_entry(entry_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('DELETE FROM sleep_entries WHERE id = ?', (entry_id,))
    return redirect(url_for('logs'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
