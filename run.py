from logging import debug
import os

from flask_socketio import SocketIO

from app import create_app, wss
from flask_admin import Admin

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)
wss.init_app(app)

if __name__ == '__main__':
    wss.run(app, debug=True)