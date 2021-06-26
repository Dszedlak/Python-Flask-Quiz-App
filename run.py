# run.py
import os

from app import create_app
from flask_admin import Admin

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(port=80)