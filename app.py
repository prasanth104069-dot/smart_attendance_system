from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'mysecretkey123'

students = [
    { 'id': 1, 'regNo': 'SKP2201', 'name': 'Arun Kumar',  'dept': 'ECE' },
    { 'id': 2, 'regNo': 'SKP2202', 'name': 'Priya Devi',  'dept': 'ECE' },
    { 'id': 3, 'regNo': 'SKP2203', 'name': 'Rahul Singh', 'dept': 'ECE' },
    { 'id': 4, 'regNo': 'SKP2204', 'name': 'Sneha Rajan', 'dept': 'ECE' },
    { 'id': 5, 'regNo': 'SKP2205', 'name': 'Karthik M',   'dept': 'ECE' },
    { 'id': 6, 'regNo': 'SKP2206', 'name': 'Divya S',     'dept': 'ECE' },
    { 'id': 7, 'regNo': 'SKP2207', 'name': 'Vikram P',    'dept': 'ECE' },
    { 'id': 8, 'regNo': 'SKP2208', 'name': 'Anitha R',    'dept': 'ECE' },
]

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
    return render_template('dashboard.html',
                           staff_name=session['staff_name'],
                           total_students=len(students))

@app.route('/mark-attendance')
def mark_attendance():
    if 'staff_name' not in session:
        return redirect(url_for('login'))
    return render_template('attendance.html')


@app.route('/view-reports')
def view_reports():
    if 'staff_name' not in session:
        return redirect(url_for('login'))
    return render_template('report.html')
        

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)