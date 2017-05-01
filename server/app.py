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
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from flask_session import Session
from .lib import db, kvs, Auth, AuthError, User, Timeline


# configuration
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
    return render_template('timeline.html', timeline=Timeline.following(g.auth.user))


@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    return render_template('timeline.html', timeline=Timeline.public())


@app.route('/<name>')
def user_timeline(name):
    """Display's a users tweets."""
    user = User.find_by('name', name)
    if user is None:
        abort(404)
    followed = False
    if g.auth.authorized():
        followed = db.query('SELECT 1 FROM followers WHERE followers.who_id = %s AND followers.whom_id = %s',
                            [g.auth.user.id, user.id], one=True) is not None
    return render_template('timeline.html', timeline=Timeline.user(user), followed=followed)


@app.route('/<name>/follow')
def follow_user(name):
    """Adds the current user as follower of the given user."""
    if not g.auth.authorized():
        abort(401)
    whom = User.find_by('name', name)
    if whom is None:
        abort(404)
    db.cur.execute('INSERT INTO followers (who_id, whom_id) values (%s, %s)', [g.auth.user.id, whom.id])
    db.conn.commit()
    flash('You are now following "%s"' % name)
    return redirect(url_for('user_timeline', name=name))


@app.route('/<name>/unfollow')
def unfollow_user(name):
    """Removes the current user as follower of the given user."""
    if not g.auth.authorized():
        abort(401)
    whom = User.find_by('name', name)
    if whom is None:
        abort(404)
    db.cur.execute('DELETE FROM followers WHERE who_id=%s AND whom_id=%s', [g.auth.user.id, whom.id])
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
          VALUES (%s, %s, %s)''', (g.auth.user.id, request.form['text'], int(time.time())))
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
