from flask import Blueprint, render_template, request, redirect, session, url_for
from app import workers, employers, job_listings, job_applications

app_routes = Blueprint("app_routes", __name__)

@app_routes.route('/')
def select_user_type():
    return render_template('select_user_type.html')

@app_routes.route('/login', methods=['GET', 'POST'])
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
                return redirect(url_for('app_routes.dashboard'))
            elif user_type == 'employer':
                return redirect(url_for('app_routes.employer_dashboard'))
        else:
            return render_template('login.html', error_message="Invalid username/password")
    return render_template('login.html', user_type=user_type)

@app_routes.route('/worker_dashboard')
def dashboard():
    if 'username' in session:
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
        pending_jobs = [job for job in job_listings if any(app['worker'] == worker and app['job_id'] == job['id'] for app in job_applications)]
        return render_template('pending_applications.html', pending_jobs=pending_jobs)
    return redirect(url_for('app_routes.select_user_type'))

@app_routes.route('/job/<int:job_id>/apply', methods=['GET', 'POST'])
def job_apply(job_id):
    if request.method == 'POST':
        return redirect(url_for('app_routes.submit_job_apply', job_id=job_id))
    
    job = next((job for job in job_listings if job['id'] == job_id), None)
    if job is None:
        return 'Job not found'
    
    return render_template('job_apply.html', job=job)

@app_routes.route('/submit_job_apply/<int:job_id>', methods=['POST'])
def submit_job_apply(job_id):
    if 'username' not in session:
        return redirect(url_for('app_routes.select_user_type'))
    
    worker = session['username']
    
    # Check if the job ID exists in the job listings
    job = next((job for job in job_listings if job['id'] == job_id), None)
    if job is None:
        return 'Job not found'

    # Check if the worker has already applied for this job
    if any(app['worker'] == worker and app['job_id'] == job_id for app in job_applications):
        return 'You have already applied for this job'

    # Add the job application to the list
    job_applications.append({'worker': worker, 'job_id': job_id})
    return redirect(url_for('app_routes.dashboard'))

@app_routes.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('app_routes.select_user_type'))