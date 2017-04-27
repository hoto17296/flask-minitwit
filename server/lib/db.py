import os
import psycopg2
import psycopg2.extras

conn = psycopg2.connect(os.environ.get('DATABASE_URL', 'postgresql://localhost/minitwit'))
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def query(query, args=(), one=False):
    cur.execute(query, args)
    return cur.fetchone() if one else cur.fetchall()
