# app/home/views.py

from flask import render_template

from . import home


@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template('home/index.html', title="Welcome")


@home.route('/quiz')
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    return render_template('home/quiz.html', title="Dashboard")

@home.route('/quiz-admin')
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    return render_template('home/quizAdmin.html', title="Quiz Admin")
