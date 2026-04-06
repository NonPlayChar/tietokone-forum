import sqlite3
from functions import hashit, token


def get_db():
    """Return a database connection with foreign keys enabled."""
    db = sqlite3.connect('database.db')
    db.execute('PRAGMA foreign_keys = ON')
    return db


def to_dict(key, value) -> dict:
    return {key[i]: value[i] for i in range(len(key))}


def initiate_database() -> None:
    print('database: Initiating database')

    with sqlite3.connect('database.db') as conn, open('schema.sql', 'r') as f:
        conn.execute('PRAGMA foreign_keys = ON')
        schema = f.read()
        conn.executescript(schema)
    
    conn.close()
    print('database: Ready!')




def create_user(uname, pswrd, pfp=None):
    username, password, uid = uname, hashit(pswrd), token(fetch_userids())
    
    db = get_db()
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
    db = get_db()
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
    db = get_db()
    cursor = db.cursor()
    fetch_result = cursor.execute('''SELECT userid, username, password, pfp, joindate FROM userdata
               WHERE userid = ?
               ''', (uid,)).fetchall()[0]
    column_names = [description[0] for description in cursor.description]
    return to_dict(column_names, fetch_result)


def fetch_userids() -> list:
    db = get_db()
    userids = db.execute('''SELECT userid FROM userdata''').fetchall()
    return userids


def create_post(uid: int, t, d):
    db = get_db()
    db.execute('''INSERT INTO posts
                (postid, userid, title, content, timestamp) VALUES (?, ?, ?, ?, datetime('now'))
                ''', (token(fetch_postids()), int(uid), t, d))
    db.commit()
    db.close()


def update_content(content, postid):
    db = get_db()
    db.execute('''
            UPDATE posts SET content = ? WHERE postid = ?
    ''', (content, postid))
    db.commit()
    db.close()
    return True


def delete_post(postid):
    try:
        db = get_db()
        db.execute('DELETE FROM posts WHERE postid = ?', (postid, ))
        db.commit()
        db.close()
        return True
    except Exception as e:
        print('Error:', e)
        db.close()
        return False


def fetch_post(postid: int):
    db = get_db()
    cursor = db.cursor()
    fetch_result = cursor.execute('SELECT postid, userid, title, content, timestamp FROM posts WHERE postid = ?', (postid, )).fetchall()[0]
    column_names = [description[0] for description in cursor.description]
    return to_dict(column_names, fetch_result)


def fetch_postids() -> list:
    db = get_db()
    postids = db.execute('''SELECT postid FROM posts''').fetchall()
    return postids


def fetch_userposts(userid: int) -> list:
    db = get_db()
    cursor = db.cursor()
    userposts = cursor.execute('SELECT postid, userid, title, content, timestamp FROM posts WHERE userid = ? ORDER BY timestamp DESC', (userid, ))

    column_names = [description[0] for description in cursor.description]
    posts = list()

    for post in userposts:
        posts.append(to_dict(column_names, post))
    return posts


def fetch_posts():
    db = get_db()
    cursor = db.cursor()
    scan = cursor.execute("SELECT postid, userid, title, content, timestamp FROM posts ORDER BY timestamp DESC")

    column_names = [description[0] for description in cursor.description]
    posts = list()

    for post in scan:
        
        posts.append(to_dict(column_names, post))

    return posts


def search_post(query):
    db = get_db()
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


def create_comment(uid, postid, comment):
    db = get_db()
    db.execute('''INSERT INTO comments
                (commentid, postid, userid, content, timestamp) VALUES (?, ?, ?, ?, datetime('now'))
                ''', (token(fetch_commentids()), postid, uid, comment))
    db.commit()
    db.close()


def fetch_commentids() -> list:
    db = get_db()
    commentids = db.execute('''SELECT commentid FROM comments''').fetchall()
    return commentids


def fetch_comments(postid):
    db = get_db()
    cursor = db.cursor()
    fetch_result = cursor.execute('SELECT commentid, postid, userid, content, timestamp FROM comments WHERE postid = ? ORDER BY timestamp DESC', (postid, )).fetchall()
    column_names = [description[0] for description in cursor.description]
    comments = list()
    for comment in fetch_result:
        comments.append(to_dict(column_names, comment))
    return comments