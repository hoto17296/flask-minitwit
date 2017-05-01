# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from flask_session import Session
from .lib import tasks, kvs, Auth, AuthError, User, Timeline


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
    following = False
    if g.auth.authorized():
        following = g.auth.user.is_following(user)
    return render_template('timeline.html', timeline=Timeline.user(user), following=following)


@app.route('/<name>/follow')
def follow_user(name):
    """Adds the current user as follower of the given user."""
    if not g.auth.authorized():
        abort(401)
    user = User.find_by('name', name)
    if user is None:
        abort(404)
    g.auth.user.follow(user)
    flash('You are now following "%s"' % name)
    return redirect(url_for('user_timeline', name=name))


@app.route('/<name>/unfollow')
def unfollow_user(name):
    """Removes the current user as follower of the given user."""
    if not g.auth.authorized():
        abort(401)
    user = User.find_by('name', name)
    if user is None:
        abort(404)
    g.auth.user.unfollow(user)
    flash('You are no longer following "%s"' % name)
    return redirect(url_for('user_timeline', name=name))


@app.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if not g.auth.authorized():
        abort(401)
    if request.form['text']:
        g.auth.user.post_message(request.form['text'])
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
