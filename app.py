from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
from datetime import date

app = Flask(__name__)
app.secret_key = 'mysecretkey123'

DATABASE = 'attendance.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_no   TEXT UNIQUE NOT NULL,
            name     TEXT NOT NULL,
            dept     TEXT NOT NULL,
            password TEXT NOT NULL DEFAULT '123456'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            status     TEXT NOT NULL,
            date       TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] == 0:
        students = [
            ('SKP2201', 'Arun Kumar',  'ECE', '123456'),
            ('SKP2202', 'Priya Devi',  'ECE', '123456'),
            ('SKP2203', 'Rahul Singh', 'ECE', '123456'),
            ('SKP2204', 'Sneha Rajan', 'ECE', '123456'),
            ('SKP2205', 'Karthik M',   'ECE', '123456'),
            ('SKP2206', 'Divya S',     'ECE', '123456'),
            ('SKP2207', 'Vikram P',    'ECE', '123456'),
            ('SKP2208', 'Anitha R',    'ECE', '123456'),
        ]
        cursor.executemany(
            'INSERT INTO students (reg_no, name, dept, password) VALUES (?, ?, ?, ?)',
            students
        )

    conn.commit()
    conn.close()

init_db()

# ─── Routes ───────────────────────────────────────────────

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id  = request.form.get('staff_id')
        password = request.form.get('password')

        # Staff login
        if user_id == 'admin' and password == 'admin123':
            session['staff_name'] = 'Admin'
            session['role'] = 'staff'
            return redirect(url_for('dashboard'))

        # Student login
        conn = get_db()
        student = conn.execute(
            'SELECT * FROM students WHERE reg_no = ? AND password = ?',
            (user_id, password)
        ).fetchone()
        conn.close()

        if student:
            session['student_id']   = student['id']
            session['student_name'] = student['name']
            session['student_reg']  = student['reg_no']
            session['role']         = 'student'
            return redirect(url_for('student_portal'))

        flash('Invalid credentials. Try again.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    conn = get_db()
    total_students = conn.execute(
        'SELECT COUNT(*) FROM students'
    ).fetchone()[0]
    conn.close()
    return render_template('dashboard.html',
                           staff_name=session['staff_name'],
                           total_students=total_students)


@app.route('/mark-attendance')
def mark_attendance():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    return render_template('attendance.html')


@app.route('/save-attendance', methods=['POST'])
def save_attendance():
    if session.get('role') != 'staff':
        return jsonify({'success': False}), 401

    data = request.get_json()
    today = date.today().isoformat()

    conn = get_db()
    conn.execute('DELETE FROM attendance WHERE date = ?', (today,))
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
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    return render_template('report.html')


@app.route('/search-attendance')
def search_attendance():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    return render_template('search.html')


@app.route('/student-portal')
def student_portal():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    return render_template('student_portal.html')


# ─── API Routes ───────────────────────────────────────────

@app.route('/api/students')
def api_students():
    if session.get('role') != 'staff':
        return jsonify([]), 401
    conn = get_db()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return jsonify([dict(s) for s in students])


@app.route('/api/report')
def api_report():
    if session.get('role') != 'staff':
        return jsonify([]), 401
    date_param = request.args.get('date', '')
    conn = get_db()
    records = conn.execute('''
        SELECT s.reg_no, s.name, s.dept, a.status, a.date
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ?
        ORDER BY s.reg_no
    ''', (date_param,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in records])


@app.route('/api/search')
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


@app.route('/api/student-portal')
def api_student_portal():
    if session.get('role') != 'student':
        return jsonify({'success': False}), 401

    conn = get_db()
    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (session['student_id'],)
    ).fetchone()

    records = conn.execute('''
        SELECT a.status, a.date
        FROM attendance a
        WHERE a.student_id = ?
        ORDER BY a.date DESC
    ''', (session['student_id'],)).fetchall()
    conn.close()

    total   = len(records)
    present = sum(1 for r in records if r['status'] == 'present')
    absent  = total - present
    percent = round((present / total * 100), 1) if total > 0 else 0

    return jsonify({
        'success': True,
        'student': dict(student),
        'records': [dict(r) for r in records],
        'total':   total,
        'present': present,
        'absent':  absent,
        'percent': percent
    })


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)