from . import db, User, Message

PER_PAGE = 30


class Timeline:
    def __init__(self, messages, type, user=None):
        self.messages = messages
        self.type = type
        self.user = user

    def to_dict(self):
        return {
            'messages': [msg.to_dict() for msg in self.messages],
            'type': self.type,
            'user': self.user.to_dict() if self.user else None,
        }

    @classmethod
    def public(cls):
        messages = db.query('''
            SELECT messages.*, users.name, users.email
            FROM messages
            JOIN users ON messages.user_id = users.id
            ORDER BY messages.pub_date DESC
            LIMIT %s''', [PER_PAGE])
        return cls(list(map(cls.format_message, messages)), 'public')

    @classmethod
    def user(cls, user):
        messages = db.query('''
            SELECT messages.*, users.name, users.email
            FROM messages
            JOIN users ON users.id = messages.user_id
            WHERE users.id = %s
            ORDER BY messages.pub_date DESC
            LIMIT %s''', [user.id, PER_PAGE])
        return cls(list(map(cls.format_message, messages)), 'user', user)

    @classmethod
    def following(cls, user):
        messages = db.query('''
            SELECT messages.*, users.name, users.email
            FROM messages
            JOIN users ON messages.user_id = users.id
            WHERE users.id = %s
               OR users.id IN (SELECT whom_id FROM followers WHERE who_id = %s)
            ORDER BY messages.pub_date DESC
            LIMIT %s''', [user.id, user.id, PER_PAGE])
        return cls(list(map(cls.format_message, messages)), 'following', user)

    @staticmethod
    def format_message(message):
        user = {
            'id': message['user_id'],
            'name': message['name'],
            'email': message['email'],
        }
        message = {
            'id': message['id'],
            'user_id': message['user_id'],
            'text': message['text'],
            'pub_date': message['pub_date'],
        }
        return Message(message, User(user))
