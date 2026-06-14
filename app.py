from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'mysecretkey123'

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
                           total_students=3)

<<<<<<< HEAD
@app.route('/mark-attendance')
def mark_attendance():
    if 'staff_name' not in session:
        return redirect(url_for('login'))
    return render_template('attendance.html')
                               

=======
>>>>>>> ce2fca456e25c5a98ff162f9c375416eb8429c21
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
<<<<<<< HEAD
    app.run(debug=True)
=======
    app.run(debug=True)
>>>>>>> ce2fca456e25c5a98ff162f9c375416eb8429c21
