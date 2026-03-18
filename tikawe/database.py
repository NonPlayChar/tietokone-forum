import sqlite3
from functions import hashit, token


def initiate_database() -> None:
    print('database: Initiating database')
    db = sqlite3.connect('database.db')

    db.execute('''CREATE TABLE IF NOT EXISTS userdata (
        userid MEDIUMINT PRIMARY KEY,
        username VARCHAR(20) UNIQUE,
        password TINYTEXT
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
            (userid, username, password) VALUES (?, ?, ?)
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