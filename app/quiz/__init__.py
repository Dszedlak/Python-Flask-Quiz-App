# app/home/__init__.py

from flask import Blueprint

quiz = Blueprint('quiz', __name__)

from . import views