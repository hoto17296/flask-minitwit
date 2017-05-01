import re
from . import db


class User:
    def __init__(self, user):
        self.id = user['id']
        self.name = user['name']
        self.email = user['email']
        self.pw_hash = user['pw_hash']

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
