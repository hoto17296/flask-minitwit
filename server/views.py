from flask import request, session, url_for, redirect, render_template, abort, g, flash
from . import app
from .lib import Auth, AuthError, User, Timeline


@app.before_request
def before_request():
    g.auth = Auth(session, app.config.get('SECRET_KEY'))


@app.route('/')
def timeline():
    if not g.auth.authorized():
        return redirect(url_for('public_timeline'))
    return render_template('timeline.html', timeline=Timeline.following(g.auth.user))


@app.route('/public')
def public_timeline():
    return render_template('timeline.html', timeline=Timeline.public())


@app.route('/<name>')
def user_timeline(name):
    user = User.find_by('name', name)
    if user is None:
        abort(404)
    following = False
    if g.auth.authorized():
        following = g.auth.user.is_following(user)
    return render_template('timeline.html', timeline=Timeline.user(user), following=following)


@app.route('/<name>/follow')
def follow_user(name):
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
    if not g.auth.authorized():
        abort(401)
    if request.form['text']:
        g.auth.user.post_message(request.form['text'])
        flash('Your message was recorded')
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
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
    flash('You were logged out')
    g.auth.logout()
    return redirect(url_for('public_timeline'))
