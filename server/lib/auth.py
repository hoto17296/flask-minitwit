from hashlib import sha256
from . import User


class AuthError(Exception):
    pass


class Auth:
    def __init__(self, store, salt='', key='user_id'):
        self.store = store
        self.salt = salt
        self.key = key
        self.user = User.find_by('id', store[key]) if key in store else None

    def authorized(self):
        return self.user is not None

    def generate_pw_hash(self, password):
        return sha256((self.salt + password).encode('utf-8')).hexdigest()

    def check_name_is_available(self, name):
        return User.find_by('name', name) is None

    def login(self, name, password):
        user = User.find_by('name', name)
        if user is None:
            raise AuthError('Invalid name')
        elif user.pw_hash != self.generate_pw_hash(password):
            raise AuthError('Invalid password')
        else:
            self.store[self.key] = user.id
            return user

    def logout(self):
        self.store.pop(self.key, None)

    def register(self, user):
        if not user['name']:
            raise AuthError('Name is required')
        elif not user['email'] or '@' not in user['email']:
            raise AuthError('E-mail address is invalid')
        elif not user['password']:
            raise AuthError('Password is required')
        elif not self.check_name_is_available(user['name']):
            raise AuthError('The name is already taken')
        else:
            pw_hash = self.generate_pw_hash(user['password'])
            return User.create(user['name'], user['email'], pw_hash)
