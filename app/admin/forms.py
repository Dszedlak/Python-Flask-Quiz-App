# app/auth/forms.py
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
