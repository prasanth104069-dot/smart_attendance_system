from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'mysecretkey123'

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        password = request.form.get('password')

        if staff_id == 'admin' and password == 'admin123':
            flash('Login successful!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid credentials. Try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)