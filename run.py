# run.py
from logging import debug
import os

from flask_socketio import SocketIO

from app import create_app
from flask_admin import Admin
from app.quiz.forms import socketio

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

if __name__ == '__main__':
    #app.run(port=80)
    socketio.run(app, debug=True)