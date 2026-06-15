from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
from datetime import date

app = Flask(__name__)
app.secret_key = 'mysecretkey123'

# Database path
DATABASE = 'attendance.db'

# ─── Database Setup ───────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_no   TEXT UNIQUE NOT NULL,
            name     TEXT NOT NULL,
            dept     TEXT NOT NULL
        )
    ''')

    # Attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            status     TEXT NOT NULL,
            date       TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')

    # Insert students if empty
    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] == 0:
        students = [
            ('SKP2201', 'Arun Kumar',  'ECE'),
            ('SKP2202', 'Priya Devi',  'ECE'),
            ('SKP2203', 'Rahul Singh', 'ECE'),
            ('SKP2204', 'Sneha Rajan', 'ECE'),
            ('SKP2205', 'Karthik M',   'ECE'),
            ('SKP2206', 'Divya S',     'ECE'),
            ('SKP2207', 'Vikram P',    'ECE'),
            ('SKP2208', 'Anitha R',    'ECE'),
        ]
        cursor.executemany(
            'INSERT INTO students (reg_no, name, dept) VALUES (?, ?, ?)',
            students
        )

    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# ─── Routes ───────────────────────────────────────────────
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        password = request.form.get('password')

        if staff_id == 'admin' and password == 'admin123':
            session['staff_name'] = 'Admin'
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'staff_name' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    total_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    conn.close()

    return render_template('dashboard.html',
                           staff_name=session['staff_name'],
                           total_students=total_students)


@app.route('/mark-attendance')
def mark_attendance():
    if 'staff_name' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()

    return render_template('attendance.html', students=students)


@app.route('/save-attendance', methods=['POST'])
def save_attendance():
    if 'staff_name' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    data = request.get_json()
    today = date.today().isoformat()

    conn = get_db()

    # Delete today's existing attendance to avoid duplicates
    conn.execute('DELETE FROM attendance WHERE date = ?', (today,))

    # Save new attendance
    for record in data:
        conn.execute(
            'INSERT INTO attendance (student_id, status, date) VALUES (?, ?, ?)',
            (record['student_id'], record['status'], today)
        )

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Attendance saved!'})


@app.route('/view-reports')
def view_reports():
    if 'staff_name' not in session:
        return redirect(url_for('login'))

    today = date.today().isoformat()
    conn = get_db()

    records = conn.execute('''
        SELECT s.reg_no, s.name, s.dept, a.status, a.date
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ?
        ORDER BY s.reg_no
    ''', (today,)).fetchall()

    conn.close()

    return render_template('report.html', records=records, today=today)


@app.route('/search-attendance')
def search_attendance():
    if 'staff_name' not in session:
        return redirect(url_for('login'))
    return render_template('search.html')


@app.route('/api/search', methods=['GET'])
def api_search():
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify([])

    conn = get_db()
    records = conn.execute('''
        SELECT s.reg_no, s.name, s.dept, a.status, a.date
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE s.reg_no LIKE ? OR s.name LIKE ?
        ORDER BY a.date DESC
    ''', (f'%{query}%', f'%{query}%')).fetchall()
    conn.close()

    return jsonify([dict(r) for r in records])


@app.route('/api/students')
def api_students():
    if 'staff_name' not in session:
        return jsonify([]), 401
    conn = get_db()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return jsonify([dict(s) for s in students])


@app.route('/api/report')
def api_report():
    if 'staff_name' not in session:
        return jsonify([]), 401
    date = request.args.get('date', '')
    conn = get_db()
    records = conn.execute('''
        SELECT s.reg_no, s.name, s.dept, a.status, a.date
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ?
        ORDER BY s.reg_no
    ''', (date,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in records])    


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)