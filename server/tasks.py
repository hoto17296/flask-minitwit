from . import app
from .lib import db


@app.cli.command('initdb')
def initdb_command():
    with open('server/schema.sql', 'r') as f:
        db.cur.execute(f.read())
    db.conn.commit()
    print('Initialized the database.')
