from datetime import datetime
from commp.src.db import get_db
from flask import flash


def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def insert_people_one(username=None, fname=None, price=None):
    db = get_db()
    error = None

    if not username:
        error = "Username is required."
    elif (
            db.execute("SELECT lname FROM people WHERE lname = ?", (username,)).fetchone()
            is not None
    ):
        error = f"User {username} is already registered."
    if error is None:
        db.execute(
            "INSERT INTO people (lname, fname, price, timestamp) VALUES (?, ?, ?, ?)",
                (username, fname, price, get_timestamp()),
        )
        db.commit()
        return True
    flash(error)
    return False

