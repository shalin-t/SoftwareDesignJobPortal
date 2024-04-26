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
def home():
    return render_template('homepage.html')

@app_routes.route('/select_user_type')
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

#new dashboard logic
@app_routes.route('/employer_dashboard')
def employer_dashboard():
    if 'username' not in session:
        return redirect(url_for('app_routes.select_user_type'))
    username = session['username']

    #fetch job listings
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_listings WHERE created_by = ?", (username,))
    job_listings = cursor.fetchall()
    conn.close()

    return render_template('employer_dashboard.html', username=username, job_listings=job_listings)

'''
@app_routes.route('/employer_dashboard')
def employer_dashboard():
    if 'username' not in session:
        return redirect(url_for('app_routes.select_user_type'))

    username = session['username']
    return render_template('employer_dashboard.html', username=username)'''

@app_routes.route('/create_job_listing', methods=['GET', 'POST'])
def create_job_listing():
    if 'username' not in session:
        return redirect(url_for('app_routes.select_user_type'))
    if request.method == 'POST':
        #get form data to create job listing record
        title = request.form['title']
        description = request.form['description']
        wage = request.form['wage']
        location = request.form['location']
        created_by = session['username'] #record logged-in user key

        #insert record into database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO job_listings (title, description, wage, location, created_by) VALUES (?, ?, ?, ?, ?)",
            (title, description, wage, location, created_by)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('app_routes.employer_dashboard'))
    return render_template('create_job_listing.html')


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
    #additional input fields being recorded
    name = request.form['name']
    email = request.form['email']


    cursor.execute(
        "INSERT INTO job_applications (worker_id, job_id, name, email) VALUES (?, ?, ?, ?)",
        (worker, job_id, name, email)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('app_routes.worker_dashboard'))

@app_routes.route('/employer_dashboard/pending_applicants/<int:job_id>')
def pending_applicants(job_id):
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('app_routes.select_user_type'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify that the job exists and is owned by the logged-in employer
    cursor.execute("SELECT * FROM job_listings WHERE id = ? AND created_by = ?", (job_id, username))
    job = cursor.fetchone()

    if not job:
        conn.close()
        return "Job not found or you do not have permission to view this job."

    # Retrieve pending applicants for this job
    cursor.execute(
        """
        SELECT ua.worker_id AS userid, ua.name, ua.email 
        FROM job_applications AS ua 
        WHERE ua.job_id = ?
        """,
        (job_id,)
    )
    pending_applicants = cursor.fetchall()
    conn.close()

    return render_template(
        'pending_applicants.html',
        job=job,
        pending_applicants=pending_applicants
    )

'''
@app_routes.route('/employer_dashboard/pending_applicants/<int:job_id>')
def pending_applicants(job_id):
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('app_routes.select_user_type'))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify that the job exists and is owned by the logged-in employer
    cursor.execute("SELECT * FROM job_listings WHERE id = ? AND employer_username = ?", (job_id, username))
    job = cursor.fetchone()

    if not job:
        conn.close()
        return "Job not found or you do not have permission to view this job."

    # Retrieve pending applicants for this job
    cursor.execute(
        """
        SELECT ua.worker_id AS userid, ua.name, ua.email 
        FROM job_applications AS ua 
        WHERE ua.job_id = ?
        """,
        (job_id,)
    )
    pending_applicants = cursor.fetchall()
    conn.close()

    return render_template(
        'pending_applicants.html',
        job=job,
        pending_applicants=pending_applicants
    )
'''
@app_routes.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('app_routes.select_user_type'))

