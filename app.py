from flask import Flask, render_template, request, redirect, session, url_for
from routes import *

app = Flask(__name__)
app.secret_key = "secretkey"

# Mock user database
workers = {'worker1': 'password1', 'worker2': 'password2', '1':'1'}
employers = {'employer1': 'password1', 'employer2': 'password2'}

# Mock job listings
job_listings = [
    {'id': 1, 'title': 'Dog Walker', 'description': 'Walk the dogs. Pick up droppings. Get money.', 'wage': '$20/hour', 'location': 'New York City'},
    {'id': 2, 'title': 'Lawn Mower', 'description': 'Mow the lawn, lemonade complimentary.', 'wage': '$25/hour', 'location': 'Los Angeles'},
    {'id': 3, 'title': 'Software Engineer', 'description': 'Fix Bugs', 'wage': '$18/hour', 'location': 'Chicago'},
    {'id': 4, 'title': 'Chef', 'description': 'Prepare and cook food, maintain clean work space.', 'wage': '$16/hour', 'location': 'Boston'},
    {'id': 5, 'title': 'Private Investigator', 'description': 'Catch the bad guys.', 'wage': '$27/hour', 'location': 'Bridgeport'},
    {'id': 6, 'title': 'University Professor', 'description': 'Lecture and give tests', 'wage': '$31/hour', 'location': 'Providence'},
]

# Mock pending applications
job_applications = [
    {'worker': 'worker1', 'job_id': 1},
    {'worker': 'worker2', 'job_id': 2},
    {'worker': 'worker1', 'job_id': 3},
]

if __name__ == '__main__':
    app.register_blueprint(app_routes)
    app.run(debug=True)
