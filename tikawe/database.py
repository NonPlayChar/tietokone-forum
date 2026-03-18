import sqlite3
from functions import hashit, token


def initiate_database() -> None:
    print('database: Initiating database')
    db = sqlite3.connect('database.db')

    db.execute('''CREATE TABLE IF NOT EXISTS userdata (
        userid MEDIUMINT PRIMARY KEY,
        username NVARCHAR(20) UNIQUE NOT NULL,
        password TINYTEXT NOT NULL,
        joindate VARCHAR(20)
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS posts (
        postid INTEGER PRIMARY KEY,
        userid INTEGER,
        timestamp INT,
        FOREIGN KEY (userid) REFERENCES userdata(userid)
    )''')
    db.close()
    print('database: Ready!')

def create_user(uname, pswrd) -> None:
    username, password, uid = uname, hashit(pswrd), token(fetch_userids())
    
    db = sqlite3.connect('database.db')
    try:
        db.execute('''INSERT INTO userdata
            (userid, username, password, joindate) VALUES (?, ?, ?, datetime('now'))
        ''', (uid, username, password))
    except sqlite3.IntegrityError as e:
        db.close()
        return Exception('Username already in use!')
    db.commit()
    db.close()

def fetch_userids() -> list:
    db = sqlite3.connect('database.db')
    userids = db.execute('''SELECT userid FROM userdata''').fetchall()
    return userids

def fetch_user(uid):
    db = sqlite3.connect('database.db')
    result = db.execute('''SELECT username FROM userdata
               WHERE userid = ?
               ''', (uid,)).fetchone()[0]
    return result

def login_user(uname, pswrd) -> any:
    db = sqlite3.connect('database.db')
    epwrd = hashit(pswrd)
    result = db.execute('''SELECT * FROM userdata
               WHERE username = ?
               ''', (uname,)).fetchall()
    print(result)
    if len(result) == 0:
        return ValueError('Invalid username or password!')
    result = result[0]
    print(result)
    print(epwrd == result[2])
    if epwrd == result[2]:
        return result[0:2]
    return ValueError('Invalid username or password!')

