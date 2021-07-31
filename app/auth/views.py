# app/auth/views.py

from operator import is_
from flask import flash, redirect, render_template, url_for, request
from flask.globals import session
from flask_login import login_required, login_user, logout_user
import json
from . import auth
from .forms import LoginForm, RegistrationForm
from .. import db
from ..models import User, clear_session, quizadminhash, adminHash


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add a user to the database through the registration form
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                            password=form.password.data,
                            is_quiz_admin=0,
                            is_admin=0, 
                            quizes_won=0,
                            quizes_hosted=0,
                            game_state=0,
                            is_present=0, 
                            is_ready=0
                            )


        # add employee to the database
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered! You may now login.')

        # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log an employee in through the login form
    """
    form = LoginForm()
    if form.validate_on_submit():

        # check whether employee exists in the database and whether
        # the password entered matches the password in the database
        user = User.query.filter_by(username=form.username.data).first()
        #print("__________________________________")
        #print(user.is_admin)
        #print("__________________________________")
        if user is not None and user.verify_password(
                form.password.data):
            # log employee in
            login_user(user)
            #print(user)
            #print(session)
            

            session['logged_in'] = True
            session['username'] = (str(user))

            if user.is_admin == 1:
                session['is_admin'] = adminHash
            if user.is_quiz_admin == 1:
                session['is_quiz_admin'] = quizadminhash
            
            # redirect to the dashboard page after login
            return redirect(url_for('home.dashboard'))

        # when login details are incorrect
        else:
            flash('Invalid email or password.')

    # load login template
    return render_template('auth/login.html', form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log an employee out through the logout link
    """
    logout_user()
    clear_session()
    flash('You have successfully been logged out.')

    # redirect to the login page
    return redirect(url_for('auth.login'))