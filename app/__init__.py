from flask import Flask, redirect, url_for
from flask_admin.base import AdminIndexView
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import abort
# local imports
from config import app_config
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from functools import wraps
import flask_uploads

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY']='p9Bv<3Eid9%$i01'
    app.config.from_object(app_config['development'])
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    Bootstrap(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login"
    migrate = Migrate(app, db)

    from app import models

    with app.app_context():
        db.create_all()

    from .models import User, Question
    admin = Admin(app, index_view=MyAdminIndexView())
    admin.add_view(Controller(User, db.session))
    admin.add_view(Controller(Question, db.session))


    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from .quiz import quiz as quiz_blueprint
    app.register_blueprint(quiz_blueprint)

    return app
    
class Controller(ModelView):
    def is_accessible(self):
            return current_user.is_admin == 1
    def not_auth(self):
        return "you are not authorized to use the admin dashboard"

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_admin == 1
     