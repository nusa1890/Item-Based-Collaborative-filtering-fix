from flaskr.db import get_db
from flask import session
user_id = session.get('user_id')

if user_id is None:
    g.user = None
else:
    g.user = get_db().execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()