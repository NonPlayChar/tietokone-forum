import sqlite3
from functions import hashit, token


def to_dict(key, value) -> dict:
    return {key[i]: value[i] for i in range(len(key))}


def initiate_database() -> None:
    print('database: Initiating database')

    with sqlite3.connect('database.db') as conn, open('schema.sql', 'r') as f:
        schema = f.read()
        conn.executescript(schema)
    
    conn.close()
    print('database: Ready!')




def create_user(uname, pswrd, pfp=None):
    username, password, uid = uname, hashit(pswrd), token(fetch_userids())
    
    db = sqlite3.connect('database.db')
    try:
        db.execute('''INSERT INTO userdata
            (userid, username, password, pfp, joindate) VALUES (?, ?, ?, ?, datetime('now'))
        ''', (uid, username, password, pfp))
    except sqlite3.IntegrityError:
        db.close()
        return Exception('Username already in use!')
    db.commit()
    db.close()


def login_user(uname, pswrd) -> any:
    db = sqlite3.connect('database.db')
    epwrd = hashit(pswrd)
    result = db.execute('''SELECT userid, username, password FROM userdata
               WHERE username = ?
               ''', (uname,)).fetchall()
    if len(result) == 0:
        return ValueError('Invalid username or password!')
    result = result[0]
    if epwrd == result[2]:
        return result[0:2]
    return ValueError('Invalid username or password!')


def fetch_user(uid):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    fetch_result = cursor.execute('''SELECT userid, username, password, pfp, joindate FROM userdata
               WHERE userid = ?
               ''', (uid,)).fetchall()[0]
    column_names = [description[0] for description in cursor.description]
    return to_dict(column_names, fetch_result)


def fetch_userids() -> list:
    db = sqlite3.connect('database.db')
    userids = db.execute('''SELECT userid FROM userdata''').fetchall()
    return userids


def create_post(uid: int, t, d):
    db = sqlite3.connect('database.db')
    db.execute('''INSERT INTO posts
                (postid, userid, title, content, timestamp) VALUES (?, ?, ?, ?, datetime('now'))
                ''', (token(fetch_postids()), int(uid), t, d))
    db.commit()
    db.close()


def update_content(content, postid):
    db = sqlite3.connect('database.db')
    db.execute('''
            UPDATE posts SET content = ? WHERE postid = ?
    ''', (content, postid))
    db.commit()
    db.close()
    return True


def delete_post(postid):
    try:
        db = sqlite3.connect('database.db')
        db.execute('DELETE FROM posts WHERE postid = ?', (postid, ))
        db.commit()
        db.close()
        return True
    except Exception as e:
        print('Error:', e)
        db.close()
        return False


def fetch_post(postid: int):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    fetch_result = cursor.execute('SELECT postid, userid, title, content, timestamp FROM posts WHERE postid = ?', (postid, )).fetchall()[0]
    column_names = [description[0] for description in cursor.description]
    return to_dict(column_names, fetch_result)


def fetch_postids() -> list:
    db = sqlite3.connect('database.db')
    postids = db.execute('''SELECT postid FROM posts''').fetchall()
    return postids


def fetch_userposts(userid: int) -> list:
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    userposts = cursor.execute('SELECT postid, userid, title, content, timestamp FROM posts WHERE userid = ? ORDER BY timestamp DESC', (userid, ))

    column_names = [description[0] for description in cursor.description]
    posts = list()

    for post in userposts:
        posts.append(to_dict(column_names, post))
    return posts


def fetch_posts():
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    scan = cursor.execute("SELECT postid, userid, title, content, timestamp FROM posts ORDER BY timestamp DESC")

    column_names = [description[0] for description in cursor.description]
    posts = list()

    for post in scan:
        
        posts.append(to_dict(column_names, post))

    return posts


def search_post(query):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    fetch_result = cursor.execute('''
            SELECT p.postid, p.userid, p.title, p.content, p.timestamp
            FROM posts p
            JOIN userdata u ON u.userid = p.userid        
            WHERE p.content LIKE ? OR p.title LIKE ?
            ORDER BY p.timestamp DESC''', ("%" + query + "%", "%" + query + "%")).fetchall()
    posts = list()
    column_names = [description[0] for description in cursor.description]
    for post in fetch_result:
        posts.append(to_dict(column_names, post))
    return posts





