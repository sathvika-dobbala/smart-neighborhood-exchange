from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database setup
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if they don't exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')
        conn.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
    print("Database initialized.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        conn = get_db_connection()
        conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    resources = conn.execute('SELECT * FROM resources').fetchall()
    conn.close()
    return render_template('dashboard.html', resources=resources)

@app.route('/add_resource', methods=['GET', 'POST'])
def add_resource():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        user_id = session.get('user_id')
        conn = get_db_connection()
        conn.execute('INSERT INTO resources (title, description, user_id) VALUES (?, ?, ?)', (title, description, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('add_resource.html')

@app.route('/delete_resource/<int:resource_id>', methods=['POST'])
def delete_resource(resource_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM resources WHERE id = ?', (resource_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
