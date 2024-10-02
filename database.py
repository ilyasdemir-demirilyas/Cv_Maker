import sqlite3

db_path = 'database.db'
def add_userdata(username, password, email):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO Users(username, password, email) VALUES (?, ?, ?)', (username, password, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM Users WHERE username =? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return user[0]  # Kullanıcı ID'sini döndür
    return None  # Kullanıcı yoksa None döndür

