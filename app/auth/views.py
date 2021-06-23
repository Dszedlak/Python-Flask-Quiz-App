# app/auth/views.py

from flask import flash, redirect, render_template, url_for
#from flask_login import login_required, login_user, logout_user, login_manager

from . import auth
from .forms import LoginForm, RegistrationForm
from app import engine
from app import models
from ..models import add_user, hash_pass, login_user, login_required, clear_session
import json

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add a user to the database through the registration form
    """
    form = RegistrationForm()
    if form.validate_on_submit(): 
            data = {
                    "email": form.email.data,
                    "username": form.username.data,
                    "first_name": form.first_name.data,
                    "last_name": form.last_name.data,
                    "password_hash":(hash_pass(form.password.data)),       
        }
            json_data = json.dumps(data)
            add_user(json_data)
            # redirect to the login page
            return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log a user in through the login form
    """
    form = LoginForm()

    if form.validate_on_submit():
        data = {
                "email": form.email.data,
                "password_hash":(hash_pass(form.password.data)),       
        }

        json_data = json.dumps(data)
        successful_login = login_user(json_data)
        
        if successful_login:
            return redirect(url_for('home.dashboard'))
                

    # load login template
    return render_template('auth/login.html', form=form, title='Login')

@auth.route('/logout')
@login_required
def logout():
    clear_session()
    return redirect(url_for('auth.login'))
    