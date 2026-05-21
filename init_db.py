import sqlite3

conn = sqlite3.connect('healthpilot.db')
cursor = conn.cursor()

# Users table
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
)''')

# Health records (vitals)
cursor.execute('''CREATE TABLE IF NOT EXISTS health_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    weight REAL,
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    blood_sugar INTEGER,
    notes TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)''')

# Medicine reminders
cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    medicine_name TEXT,
    dosage TEXT,
    time TEXT,
    frequency TEXT,
    is_taken INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
)''')

# Symptom check history
cursor.execute('''CREATE TABLE IF NOT EXISTS symptom_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    symptoms TEXT,
    predicted_disease TEXT,
    confidence REAL,
    date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)''')

conn.commit()
conn.close()
print("Database initialized.")