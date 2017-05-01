import os
from flask import Flask
from flask_session import Session
from .lib import kvs


SESSION_TYPE = 'redis'
SESSION_REDIS = kvs
SECRET_KEY = os.environ.get('SECRET_KEY', '')

app = Flask(__name__)
app.config.from_object(__name__)
Session(app)


import server.views  # noqa: F401
import server.tasks  # noqa: F401
