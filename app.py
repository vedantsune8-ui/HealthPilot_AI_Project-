from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import hashlib
import datetime
import joblib
import numpy as np

app = Flask(__name__)
app.secret_key = 'healthpilot_secret_key'

# Load ML model
model, symptoms_list, diseases_list = joblib.load('model.pkl')

# Database helper
def get_db():
    conn = sqlite3.connect('healthpilot.db')
    conn.row_factory = sqlite3.Row
    return conn

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return "Username already exists"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db()
    # Get latest health record
    latest_health = conn.execute("SELECT * FROM health_records WHERE user_id=? ORDER BY date DESC LIMIT 1", (user_id,)).fetchone()
    # Get upcoming reminders (not taken)
    reminders = conn.execute("SELECT * FROM reminders WHERE user_id=? AND is_taken=0", (user_id,)).fetchall()
    conn.close()
    return render_template('dashboard.html', latest_health=latest_health, reminders=reminders)

@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    bmi_result = None
    category = None
    if request.method == 'POST':
        weight = float(request.form['weight'])
        height = float(request.form['height']) / 100  # cm to m
        bmi_result = round(weight / (height * height), 1)
        if bmi_result < 18.5:
            category = "Underweight"
        elif bmi_result < 25:
            category = "Normal weight"
        elif bmi_result < 30:
            category = "Overweight"
        else:
            category = "Obese"
    return render_template('bmi.html', bmi=bmi_result, category=category)

@app.route('/symptom_check', methods=['GET', 'POST'])
def symptom_check():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    prediction = None
    confidence = None
    if request.method == 'POST':
        selected_symptoms = request.form.getlist('symptoms')
        # Create feature vector
        input_vector = [1 if sym in selected_symptoms else 0 for sym in symptoms_list]
        input_array = np.array(input_vector).reshape(1, -1)
        proba = model.predict_proba(input_array)[0]
        pred_index = np.argmax(proba)
        prediction = model.classes_[pred_index]
        confidence = round(proba[pred_index] * 100, 2)
        # Save to history
        conn = get_db()
        conn.execute("INSERT INTO symptom_checks (user_id, symptoms, predicted_disease, confidence, date) VALUES (?, ?, ?, ?, ?)",
                     (session['user_id'], ','.join(selected_symptoms), prediction, confidence, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    return render_template('symptom_check.html', symptoms=symptoms_list, prediction=prediction, confidence=confidence)

@app.route('/health_log', methods=['GET', 'POST'])
def health_log():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        weight = request.form['weight']
        bp_sys = request.form['bp_systolic']
        bp_dia = request.form['bp_diastolic']
        blood_sugar = request.form['blood_sugar']
        notes = request.form['notes']
        conn = get_db()
        conn.execute("INSERT INTO health_records (user_id, date, weight, blood_pressure_systolic, blood_pressure_diastolic, blood_sugar, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (session['user_id'], datetime.datetime.now().strftime("%Y-%m-%d"), weight, bp_sys, bp_dia, blood_sugar, notes))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('health_log.html')

@app.route('/reminders', methods=['GET', 'POST'])
def reminders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            medicine_name = request.form['medicine_name']
            dosage = request.form['dosage']
            time = request.form['time']
            frequency = request.form['frequency']
            conn.execute("INSERT INTO reminders (user_id, medicine_name, dosage, time, frequency) VALUES (?, ?, ?, ?, ?)",
                         (session['user_id'], medicine_name, dosage, time, frequency))
            conn.commit()
        elif action == 'mark_taken':
            reminder_id = request.form['reminder_id']
            conn.execute("UPDATE reminders SET is_taken=1 WHERE id=?", (reminder_id,))
            conn.commit()
        elif action == 'delete':
            reminder_id = request.form['reminder_id']
            conn.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
            conn.commit()
    reminders_list = conn.execute("SELECT * FROM reminders WHERE user_id=? ORDER BY time", (session['user_id'],)).fetchall()
    conn.close()
    return render_template('reminders.html', reminders=reminders_list)

@app.route('/report')
def report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db()
    health_records = conn.execute("SELECT * FROM health_records WHERE user_id=? ORDER BY date DESC", (user_id,)).fetchall()
    symptom_history = conn.execute("SELECT * FROM symptom_checks WHERE user_id=? ORDER BY date DESC", (user_id,)).fetchall()
    conn.close()
    return render_template('report.html', health_records=health_records, symptom_history=symptom_history)

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    conn = get_db()
    users = conn.execute("SELECT id, username, is_admin FROM users").fetchall()
    health_records = conn.execute("SELECT * FROM health_records ORDER BY date DESC").fetchall()
    reminders = conn.execute("SELECT * FROM reminders").fetchall()
    predictions = conn.execute("SELECT * FROM symptom_checks ORDER BY date DESC").fetchall()
    conn.close()
    return render_template('admin.html', users=users, health_records=health_records, reminders=reminders, predictions=predictions)

if __name__ == '__main__':
    app.run(debug=True)