import time
from . import db


class Message:
    def __init__(self, message, user=None):
        self.id = message['id']
        self.user_id = message['user_id']
        self.text = message['text']
        self.pub_date = message['pub_date']
        self.user = user

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'text': self.text,
            'pub_date': self.pub_date,
            'user': self.user.to_dict() if self.user else None
        }

    @classmethod
    def create(cls, user, text):
        query = 'INSERT INTO messages (user_id, text, pub_date) VALUES (%s, %s, %s)'
        db.cur.execute(query, (user.id, text, int(time.time())))
        db.conn.commit()
