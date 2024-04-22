from flask import Blueprint, render_template, request, redirect, session, url_for
#from app import workers, employers, job_listings, job_applications
import sqlite3

app_routes = Blueprint("app_routes", __name__)

# Function to establish connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn

@app_routes.route('/')
def select_user_type():
    return render_template('select_user_type.html')

@app_routes.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']  # Assuming you have a user type field in your registration form
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)", (username, password, user_type))
            conn.commit()
            conn.close()
            return redirect(url_for('app_routes.select_user_type'))  # Redirect to select_user_type route
        except sqlite3.IntegrityError:
            error_message = "Username already exists. Please choose a different username."
            return render_template('create_account.html', error_message=error_message)
    return render_template('create_account.html')


@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    user_type = request.args.get('type')
    if user_type == 'worker':
        table = 'workers'
    elif user_type == 'employer':
        table = 'employers'
    else:
        return 'Invalid user type123'

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE username = ? AND password = ? AND user_type = ?", (username, password, user_type))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            if user_type == 'worker':
                return redirect(url_for('app_routes.worker_dashboard'))
            elif user_type == 'employer':
                return redirect(url_for('app_routes.employer_dashboard'))
        else:
            return render_template('login.html', error_message="Invalid username/password")
    return render_template('login.html', user_type=user_type)

@app_routes.route('/worker_dashboard')
def worker_dashboard():
    if 'username' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_listings")
        job_listings = cursor.fetchall()
        conn.close()
        return render_template('worker_dashboard.html', job_listings=job_listings)
    return redirect(url_for('app_routes.select_user_type'))

@app_routes.route('/employer_dashboard')
def employer_dashboard():
    if 'username' in session:
        return 'Employer Dashboard<br><a href="/logout">Logout</a>'
    return redirect(url_for('app_routes.select_user_type'))

@app_routes.route('/pending_applications')
def pending_applications():
    if 'username' in session:
        worker = session['username']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_applications WHERE worker_id = ?", (worker,))
        job_applications = cursor.fetchall()
        pending_jobs = []
        for app in job_applications:
            cursor.execute("SELECT * FROM job_listings WHERE id = ?", (app['job_id'],))
            job = cursor.fetchone()
            if job:
                pending_jobs.append(job)
        conn.close()
        return render_template('pending_applications.html', pending_jobs=pending_jobs)
    return redirect(url_for('app_routes.select_user_type'))

@app_routes.route('/job/<int:job_id>/apply', methods=['GET', 'POST'])
def job_apply(job_id):
    if request.method == 'POST':
        return redirect(url_for('app_routes.submit_job_apply', job_id=job_id))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_listings WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    conn.close()

    if job is None:
        return 'Job not found'
    
    return render_template('job_apply.html', job=job)

@app_routes.route('/submit_job_apply/<int:job_id>', methods=['POST'])
def submit_job_apply(job_id):
    if 'username' not in session:
        return redirect(url_for('app_routes.select_user_type'))
    
    worker = session['username']

    #Checks for job ID to exist in job listings table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_listings WHERE id = ?", (job_id,))
    job = cursor.fetchone()

    if job is None:
        conn.close()
        return 'Job not found. Error.'
    
    #Check if worker has already applied to job
    cursor.execute("SELECT * FROM job_applications WHERE worker_id = ? AND job_id = ?", (worker, job_id))
    existing_application = cursor.fetchone()
    if existing_application:
        conn.close()
        return "You have already applied for this job."
    
    #After two checks passes for the user, add job to application list
    cursor.execute("INSERT INTO job_applications (worker_id, job_id) VALUES (?, ?)", (worker, job_id))
    conn.commit()
    conn.close()
    return redirect(url_for('app_routes.worker_dashboard'))

@app_routes.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('app_routes.select_user_type'))

