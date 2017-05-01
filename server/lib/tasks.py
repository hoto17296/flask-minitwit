from . import db


def init_db():
    with open('server/schema.sql', 'r') as f:
        db.cur.execute(f.read())
    db.conn.commit()
