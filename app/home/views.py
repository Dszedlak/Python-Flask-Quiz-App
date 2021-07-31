# app/home/views.py

from flask import render_template
from ..models import load_scores
from . import home

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template('home/index.html', title="Welcome")

@home.route('/dashboard')
def dashboard():
    
    scores = load_scores()

    return render_template('home/dashboard.html', scores=scores, title="Dashboard")
