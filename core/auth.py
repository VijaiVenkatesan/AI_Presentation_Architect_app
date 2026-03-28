import sqlite3
import hashlib
from core.db import init_db

DB_PATH = "/tmp/app.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def signup(username, password):
    init_db()  # ensure tables exist

    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True, "Signup successful"

    except Exception as e:
        conn.close()
        return False, str(e)


def login(username, password):
    init_db()  # ensure tables exist

    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )

    user = c.fetchone()
    conn.close()

    if user:
        return True, user
    else:
        return False, "Invalid username or password"
