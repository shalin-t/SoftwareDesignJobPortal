from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Mock user database
workers = {'worker1': 'password1', 'worker2': 'password2', '1':'1'}
employers = {'employer1': 'password1', 'employer2': 'password2'}

# Mock job listings
job_listings = [
    {'title': 'Job 1', 'description': 'Description for Job 1', 'wage': '$20/hour', 'location': 'New York'},
    {'title': 'Job 2', 'description': 'Description for Job 2', 'wage': '$25/hour', 'location': 'Los Angeles'},
    {'title': 'Job 3', 'description': 'Description for Job 3', 'wage': '$18/hour', 'location': 'Chicago'}
]

@app.route('/')
def select_user_type():
    return render_template('select_user_type.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    user_type = request.args.get('type')
    if user_type == 'worker':
        users = workers
    elif user_type == 'employer':
        users = employers
    else:
        return 'Invalid user type'

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            if user_type == 'worker':
                return redirect(url_for('dashboard'))
            elif user_type == 'employer':
                return redirect(url_for('employer_dashboard'))
        else:
            return render_template('login.html', error_message="Invalid username/password")
    return render_template('login.html', user_type=user_type)

@app.route('/worker_dashboard')
def dashboard():
    if 'username' in session:
        return render_template('worker_dashboard.html', job_listings=job_listings)
    return redirect(url_for('select_user_type'))

@app.route('/employer_dashboard')
def employer_dashboard():
    if 'username' in session:
        return 'Employer Dashboard<br><a href="/logout">Logout</a>'
    return redirect(url_for('select_user_type'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('select_user_type'))

if __name__ == '__main__':
    app.run(debug=True)
