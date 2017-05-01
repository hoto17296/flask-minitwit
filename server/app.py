# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
import time
from hashlib import md5
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from flask_session import Session
from .lib import db, kvs, Auth, AuthError


# configuration
PER_PAGE = int(os.environ.get('PER_PAGE', 30))
SESSION_TYPE = 'redis'
SESSION_REDIS = kvs
SECRET_KEY = os.environ.get('SECRET_KEY', '')

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
Session(app)


def init_db():
    with app.open_resource('schema.sql', mode='r') as f:
        db.cur.execute(f.read())
    db.conn.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')


def get_user_id(name):
    """Convenience method to look up the id for a name."""
    rv = db.query('SELECT id FROM users WHERE name = %s', [name], one=True)
    return None if rv is None else rv['id']


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'https://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


def message_to_dict(message):
    return {
        'user': {
            'name': message['name'],
            'icon_url': gravatar_url(message['email'], 48),
        },
        'text': message['text'],
        'pub_date': message['pub_date'],
    }


@app.before_request
def before_request():
    g.auth = Auth(session, SECRET_KEY)


@app.route('/')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.auth.authorized():
        return redirect(url_for('public_timeline'))
    messages = db.query('''
        SELECT messages.*, users.*
        FROM messages
        JOIN users ON messages.user_id = users.id
        WHERE users.id = %s
           OR users.id IN (SELECT whom_id FROM followers WHERE who_id = %s)
        ORDER BY messages.pub_date DESC
        LIMIT %s''', [g.auth.user['id'], g.auth.user['id'], PER_PAGE])
    return render_template('timeline.html', messages=messages)


@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    messages = db.query('''
        SELECT messages.*, users.*
        FROM messages
        JOIN users ON messages.user_id = users.id
        ORDER BY messages.pub_date DESC
        LIMIT %s''', [PER_PAGE])
    return render_template('timeline.html', messages=messages)


@app.route('/<name>')
def user_timeline(name):
    """Display's a users tweets."""
    profile_user = db.query('SELECT * FROM users WHERE name = %s', [name], one=True)
    if profile_user is None:
        abort(404)
    followed = False
    if g.auth.authorized():
        followed = db.query('SELECT 1 FROM followers WHERE followers.who_id = %s AND followers.whom_id = %s',
                            [g.auth.user['id'], profile_user['id']], one=True) is not None
    messages = db.query('''
                        SELECT messages.*, users.* FROM messages
                        JOIN users ON users.id = messages.user_id
                        WHERE users.id = %s
                        ORDER BY messages.pub_date DESC
                        LIMIT %s''',
                        [profile_user['id'], PER_PAGE])
    return render_template('timeline.html', messages=messages, followed=followed, profile_user=profile_user)


@app.route('/<name>/follow')
def follow_user(name):
    """Adds the current user as follower of the given user."""
    if not g.auth.authorized():
        abort(401)
    whom_id = get_user_id(name)
    if whom_id is None:
        abort(404)
    db.cur.execute('INSERT INTO followers (who_id, whom_id) values (%s, %s)', [g.auth.user['id'], whom_id])
    db.conn.commit()
    flash('You are now following "%s"' % name)
    return redirect(url_for('user_timeline', name=name))


@app.route('/<name>/unfollow')
def unfollow_user(name):
    """Removes the current user as follower of the given user."""
    if not g.auth.authorized():
        abort(401)
    whom_id = get_user_id(name)
    if whom_id is None:
        abort(404)
    db.cur.execute('DELETE FROM followers WHERE who_id=%s AND whom_id=%s', [g.auth.user['id'], whom_id])
    db.conn.commit()
    flash('You are no longer following "%s"' % name)
    return redirect(url_for('user_timeline', name=name))


@app.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if not g.auth.authorized():
        abort(401)
    if request.form['text']:
        db.cur.execute('''INSERT INTO messages (user_id, text, pub_date)
          VALUES (%s, %s, %s)''', (g.auth.user['id'], request.form['text'], int(time.time())))
        db.conn.commit()
        flash('Your message was recorded')
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.auth.authorized():
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        try:
            g.auth.login(request.form['name'], request.form['password'])
            flash('You were logged in')
            return redirect(url_for('timeline'))
        except AuthError as err:
            error = str(err)
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.auth.authorized():
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        try:
            if request.form['password'] != request.form['password2']:
                raise AuthError('The two passwords do not match')
            g.auth.register({
                'name': request.form['name'],
                'email': request.form['email'],
                'password': request.form['password'],
            })
            flash('You were successfully registered')
            g.auth.login(request.form['name'], request.form['password'])
            return redirect(url_for('timeline'))
        except AuthError as err:
            error = str(err)
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    g.auth.logout()
    return redirect(url_for('public_timeline'))


app.jinja_env.filters['message_to_dict'] = message_to_dict
