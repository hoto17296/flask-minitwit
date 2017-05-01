import re
from hashlib import md5
from . import db


class User:
    def __init__(self, user):
        self.id = user['id']
        self.name = user['name']
        self.email = user['email']
        self.pw_hash = user['pw_hash'] if 'pw_hash' in user else None

    def gravatar_url(self):
        hash = md5(self.email.strip().lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/%s?d=identicon' % hash

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon_url': self.gravatar_url(),
        }

    @classmethod
    def find_by(cls, col, id):
        if not re.match(r'^[a-z0-9_]+$', col):
            raise ValueError()
        user = db.query('SELECT * FROM users WHERE %s = %%s LIMIT 1' % col, [id], one=True)
        return cls(user) if user else None

    @classmethod
    def create(cls, name, email, pw_hash):
        db.cur.execute('INSERT INTO users (name, email, pw_hash) values (%s, %s, %s)', [name, email, pw_hash])
        db.conn.commit()
        return cls.find_by('name', name)
