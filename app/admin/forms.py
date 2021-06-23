# app/auth/forms.py

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
import sqlite3, os, hashlib
from flask import Flask, jsonify, render_template, request, g
import json

app = Flask(__name__)
from ..models import User

class AdminForm(FlaskForm):
    print("oof")


    #display contents of database? 
    #remove/delete users
    #give users different privs
