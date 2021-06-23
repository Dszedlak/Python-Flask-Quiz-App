# app/home/__init__.py

from flask import Blueprint

store = Blueprint('store', __name__)

from . import views