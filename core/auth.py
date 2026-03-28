import sqlite3
import hashlib

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def signup(username, password):
    conn = sqlite3.connect("app.db")
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
    conn = sqlite3.connect("app.db")
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
