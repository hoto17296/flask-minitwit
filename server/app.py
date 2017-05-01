# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from flask import Flask
from flask_session import Session
from .lib import tasks, kvs


# configuration
SESSION_TYPE = 'redis'
SESSION_REDIS = kvs
SECRET_KEY = os.environ.get('SECRET_KEY', '')

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
Session(app)


@app.cli.command('initdb')
def initdb_command():
    tasks.init_db()
    print('Initialized the database.')
