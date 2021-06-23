# app/__init__.py

# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import sys, os
import sqlite3
# local imports
from config import app_config

from flask_bootstrap import Bootstrap

#db variable initialization
engine = create_engine('sqlite:///database.db') 

def create_app(config_name):
    app = Flask(__name__)
    app.config['SECRET_KEY']='p9Bv<3Eid9%$i01'
    app.config.from_object(app_config['development'])
    
    Bootstrap(app)

    from app import models
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from.store import store as store_blueprint
    app.register_blueprint(store_blueprint)
 
    from.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)
    return app