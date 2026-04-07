import sqlite3
from functions import hashit, token


def get_db():
    """Return a database connection with foreign keys enabled."""
    try:
        db = sqlite3.connect('database.db')
        db.execute('PRAGMA foreign_keys = ON')
        return db
    except sqlite3.Error as e:
        print(f'Failed to connect to database: {e}')
        raise


def to_dict(key, value) -> dict:
    return {key[i]: value[i] for i in range(len(key))}


def initiate_database() -> None:
    print('database: Initiating database')
    try:
        with sqlite3.connect('database.db') as conn, open('schema.sql', 'r') as f:
            conn.execute('PRAGMA foreign_keys = ON')
            schema = f.read()
            conn.executescript(schema)
        print('database: Ready!')
    except FileNotFoundError:
        print('Error: schema.sql file not found.')
        raise
    except sqlite3.Error as e:
        print(f'Database error during initialization: {e}')
        raise
    except Exception as e:
        print(f'Unexpected error during database initialization: {e}')
        raise




def create_user(uname, pswrd, pfp=None):
    username, password, uid = uname, hashit(pswrd), token(fetch_userids())
    
    db = get_db()
    try:
        db.execute('''INSERT INTO userdata
            (userid, username, password, pfp, joindate) VALUES (?, ?, ?, ?, datetime('now'))
        ''', (uid, username, password, pfp))
        db.commit()
    except sqlite3.Error as e:
        print(f'Database error in create_user: {e}')
        raise
    finally:
        db.close()


def login_user(uname, pswrd) -> any:
    db = get_db()
    try:
        epwrd = hashit(pswrd)
        result = db.execute('''SELECT userid, username, password FROM userdata
                   WHERE username = ?
                   ''', (uname,)).fetchone()
        if not result or epwrd != result[2]:
            raise ValueError('Invalid username or password!')
        return result[0], result[1]
    except sqlite3.Error as e:
        print(f'Database error in login_user: {e}')
        raise
    finally:
        db.close()


def fetch_user(uid):
    db = get_db()
    try:
        cursor = db.cursor()
        fetch_result = cursor.execute('''SELECT userid, username, password, pfp, joindate FROM userdata
                   WHERE userid = ?
                   ''', (uid,)).fetchall()
        if not fetch_result:
            raise ValueError(f'User with id {uid} not found.')
        fetch_result = fetch_result[0]
        column_names = [description[0] for description in cursor.description]
        return to_dict(column_names, fetch_result)
    except sqlite3.Error as e:
        print(f'Database error in fetch_user: {e}')
        raise
    finally:
        db.close()


def fetch_userids() -> list:
    db = get_db()
    try:
        userids = db.execute('''SELECT userid FROM userdata''').fetchall()
        return userids
    except sqlite3.Error as e:
        print(f'Database error in fetch_userids: {e}')
        raise
    finally:
        db.close()


def create_post(uid: int, t, d):
    db = get_db()
    try:
        db.execute('''INSERT INTO posts
                    (postid, userid, title, content, timestamp) VALUES (?, ?, ?, ?, datetime('now'))
                    ''', (token(fetch_postids()), int(uid), t, d))
        db.commit()
    except sqlite3.Error as e:
        print(f'Database error in create_post: {e}')
        raise
    finally:
        db.close()


def update_content(title, content, postid):
    db = get_db()
    try:
        db.execute('''
                UPDATE posts SET title = ?, content = ? WHERE postid = ?
        ''', (title, content, postid))
        db.commit()
        return True
    except sqlite3.Error as e:
        print(f'Database error in update_content: {e}')
        raise
    finally:
        db.close()


def delete_post(postid):
    db = get_db()
    try:
        db.execute('DELETE FROM posts WHERE postid = ?', (postid, ))
        db.commit()
        return True
    except sqlite3.Error as e:
        print(f'Database error in delete_post: {e}')
        return False
    finally:
        db.close()


def fetch_post(postid: int):
    db = get_db()
    try:
        cursor = db.cursor()
        fetch_result = cursor.execute('SELECT postid, userid, title, content, timestamp FROM posts WHERE postid = ?', (postid, )).fetchall()
        if not fetch_result:
            raise ValueError(f'Post with id {postid} not found.')
        fetch_result = fetch_result[0]
        column_names = [description[0] for description in cursor.description]
        return to_dict(column_names, fetch_result)
    except sqlite3.Error as e:
        print(f'Database error in fetch_post: {e}')
        raise
    finally:
        db.close()


def fetch_postids() -> list:
    db = get_db()
    try:
        postids = db.execute('''SELECT postid FROM posts''').fetchall()
        return postids
    except sqlite3.Error as e:
        print(f'Database error in fetch_postids: {e}')
        raise
    finally:
        db.close()


def fetch_userposts(userid: int) -> list:
    db = get_db()
    try:
        cursor = db.cursor()
        userposts = cursor.execute('SELECT postid, userid, title, content, timestamp FROM posts WHERE userid = ? ORDER BY timestamp DESC', (userid, ))

        column_names = [description[0] for description in cursor.description]
        posts = list()

        for post in userposts:
            posts.append(to_dict(column_names, post))
        return posts
    except sqlite3.Error as e:
        print(f'Database error in fetch_userposts: {e}')
        raise
    finally:
        db.close()


def fetch_posts():
    db = get_db()
    try:
        cursor = db.cursor()
        scan = cursor.execute("SELECT postid, userid, title, content, timestamp FROM posts ORDER BY timestamp DESC")

        column_names = [description[0] for description in cursor.description]
        posts = list()

        for post in scan:
            
            posts.append(to_dict(column_names, post))

        return posts
    except sqlite3.Error as e:
        print(f'Database error in fetch_posts: {e}')
        raise
    finally:
        db.close()


def search_post(query):
    db = get_db()
    try:
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
    except sqlite3.Error as e:
        print(f'Database error in search_post: {e}')
        raise
    finally:
        db.close()


def create_comment(uid, postid, comment):
    db = get_db()
    try:
        db.execute('''INSERT INTO comments
                    (commentid, postid, userid, content, timestamp) VALUES (?, ?, ?, ?, datetime('now'))
                    ''', (token(fetch_commentids()), postid, uid, comment))
        db.commit()
    except sqlite3.Error as e:
        print(f'Database error in create_comment: {e}')
        raise
    finally:
        db.close()


def fetch_commentids() -> list:
    db = get_db()
    try:
        commentids = db.execute('''SELECT commentid FROM comments''').fetchall()
        return commentids
    except sqlite3.Error as e:
        print(f'Database error in fetch_commentids: {e}')
        raise
    finally:
        db.close()


def fetch_comments(postid):
    db = get_db()
    try:
        cursor = db.cursor()
        fetch_result = cursor.execute('SELECT commentid, postid, userid, content, timestamp FROM comments WHERE postid = ? ORDER BY timestamp DESC', (postid, )).fetchall()
        column_names = [description[0] for description in cursor.description]
        comments = list()
        for comment in fetch_result:
            comments.append(to_dict(column_names, comment))
        return comments
    except sqlite3.Error as e:
        print(f'Database error in fetch_comments: {e}')
        raise
    finally:
        db.close()


def fetch_page_stats(target_type, target_id):
    db = get_db()
    try:
        cursor = db.cursor()
        row = cursor.execute(
            'SELECT statid, target_type, target_id, visits, likes FROM page_stats WHERE target_type = ? AND target_id = ?', (target_type, target_id)).fetchone()
        if not row:
            cursor.execute(
                'INSERT INTO page_stats (target_type, target_id) VALUES (?, ?)', (target_type, target_id))
            db.commit()
            row = cursor.execute(
                'SELECT statid, target_type, target_id, visits, likes FROM page_stats WHERE target_type = ? AND target_id = ?', (target_type, target_id)).fetchone()
        column_names = [description[0] for description in cursor.description]
        result = to_dict(column_names, row)
        return result
    except sqlite3.Error as e:
        print(f'Database error in fetch_page_stats: {e}')
        raise
    finally:
        db.close()


def increment_page_visits(target_type, target_id):
    db = get_db()
    try:
        db.execute('INSERT OR IGNORE INTO page_stats (target_type, target_id) VALUES (?, ?)', (target_type, target_id))
        db.execute('UPDATE page_stats SET visits = visits + 1 WHERE target_type = ? AND target_id = ?', (target_type, target_id))
        db.commit()
    except sqlite3.Error as e:
        print(f'Database error in increment_page_visits: {e}')
        raise
    finally:
        db.close()


def increment_page_likes(target_type, target_id):
    db = get_db()
    try:
        db.execute('INSERT OR IGNORE INTO page_stats (target_type, target_id) VALUES (?, ?)', (target_type, target_id))
        db.execute('UPDATE page_stats SET likes = likes + 1 WHERE target_type = ? AND target_id = ?', (target_type, target_id))
        db.commit()
    except sqlite3.Error as e:
        print(f'Database error in increment_page_likes: {e}')
        raise
    finally:
        db.close()


def has_user_liked(target_type, target_id, userid):
    db = get_db()
    try:
        row = db.execute(
            'SELECT 1 FROM page_likes WHERE target_type = ? AND target_id = ? AND userid = ?',
            (target_type, target_id, userid)
        ).fetchone()
        return row is not None
    except sqlite3.Error as e:
        print(f'Database error in has_user_liked: {e}')
        raise
    finally:
        db.close()


def create_page_like(target_type, target_id, userid):
    db = get_db()
    try:
        db.execute(
            'INSERT INTO page_likes (userid, target_type, target_id) VALUES (?, ?, ?)',
            (userid, target_type, target_id)
        )
        db.commit()
        increment_page_likes(target_type, target_id)
        return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error as e:
        print(f'Database error in create_page_like: {e}')
        raise
    finally:
        db.close()


def decrement_page_likes(target_type, target_id):
    db = get_db()
    try:
        db.execute('INSERT OR IGNORE INTO page_stats (target_type, target_id) VALUES (?, ?)', (target_type, target_id))
        db.execute('UPDATE page_stats SET likes = CASE WHEN likes > 0 THEN likes - 1 ELSE 0 END WHERE target_type = ? AND target_id = ?', (target_type, target_id))
        db.commit()
    except sqlite3.Error as e:
        print(f'Database error in decrement_page_likes: {e}')
        raise
    finally:
        db.close()


def delete_page_like(target_type, target_id, userid):
    db = get_db()
    try:
        cursor = db.cursor()
        row = cursor.execute(
            'SELECT 1 FROM page_likes WHERE target_type = ? AND target_id = ? AND userid = ?',
            (target_type, target_id, userid)
        ).fetchone()
        if not row:
            return False

        cursor.execute(
            'DELETE FROM page_likes WHERE target_type = ? AND target_id = ? AND userid = ?',
            (target_type, target_id, userid)
        )
        db.commit()
        decrement_page_likes(target_type, target_id)
        return True
    except sqlite3.Error as e:
        print(f'Database error in delete_page_like: {e}')
        raise
    finally:
        db.close()