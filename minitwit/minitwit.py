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
import psycopg2
import psycopg2.extras
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from werkzeug import check_password_hash, generate_password_hash


# configuration
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

db_conn = psycopg2.connect(os.environ.get('DATABASE_URL', 'postgresql://localhost/minitwit'))
db_cur = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    db_cur.execute(query, args)
    return db_cur.fetchone() if one else db_cur.fetchall()


def get_user_id(name):
    """Convenience method to look up the id for a name."""
    rv = query_db('SELECT id FROM users WHERE name = %s', [name], one=True)
    return None if rv is None else rv['id']


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'https://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = query_db('SELECT * FROM users WHERE id = %s', [session['user_id']], one=True)


@app.route('/')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('public_timeline'))
    messages = query_db('''
        SELECT messages.*, users.*
        FROM messages
        JOIN users ON messages.user_id = users.id
        WHERE users.id = %s
           OR users.id IN (SELECT whom_id FROM followers WHERE who_id = %s)
        ORDER BY messages.pub_date DESC
        LIMIT %s''', [session['user_id'], session['user_id'], PER_PAGE])
    return render_template('timeline.html', messages=messages)


@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    messages = query_db('''
        SELECT messages.*, users.*
        FROM messages
        JOIN users ON messages.user_id = users.id
        ORDER BY messages.pub_date DESC
        LIMIT %s''', [PER_PAGE])
    return render_template('timeline.html', messages=messages)


@app.route('/<name>')
def user_timeline(name):
    """Display's a users tweets."""
    profile_user = query_db('SELECT * FROM users WHERE name = %s', [name], one=True)
    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        followed = query_db('SELECT 1 FROM followers WHERE followers.who_id = %s AND followers.whom_id = %s',
                            [session['user_id'], profile_user['id']], one=True) is not None
    messages = query_db('''
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
    if not g.user:
        abort(401)
    whom_id = get_user_id(name)
    if whom_id is None:
        abort(404)
    db_cur.execute('INSERT INTO followers (who_id, whom_id) values (%s, %s)', [session['user_id'], whom_id])
    db_conn.commit()
    flash('You are now following "%s"' % name)
    return redirect(url_for('user_timeline', name=name))


@app.route('/<name>/unfollow')
def unfollow_user(name):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(name)
    if whom_id is None:
        abort(404)
    db_cur.execute('DELETE FROM followers WHERE who_id=%s AND whom_id=%s', [session['user_id'], whom_id])
    db_conn.commit()
    flash('You are no longer following "%s"' % name)
    return redirect(url_for('user_timeline', name=name))


@app.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        db_cur.execute('''INSERT INTO messages (user_id, text, pub_date)
          VALUES (%s, %s, %s)''', (session['user_id'], request.form['text'], int(time.time())))
        db_conn.commit()
        flash('Your message was recorded')
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = query_db('''SELECT * FROM users WHERE name = %s''', [request.form['name']], one=True)
        if user is None:
            error = 'Invalid name'
        elif not check_password_hash(user['pw_hash'], request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user['id']
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['name']:
            error = 'You have to enter a name'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['name']) is not None:
            error = 'The name is already taken'
        else:
            pw_hash = generate_password_hash(request.form['password'])
            db_cur.execute('INSERT INTO users (name, email, pw_hash) values (%s, %s, %s)',
                           [request.form['name'], request.form['email'], pw_hash])
            db_conn.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url
