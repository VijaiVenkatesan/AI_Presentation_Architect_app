import sqlite3
import hashlib

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def signup(username, password):
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (NULL, ?, ?)",
                  (username, hash_password(password)))
        conn.commit()
        return True
    except:
        return False

def login(username, password):
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()
