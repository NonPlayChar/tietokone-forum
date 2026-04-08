import time
from flask import Flask, request, render_template, redirect, session, abort, url_for, flash
import database as db
import sqlite3
from functions import secret_key
from functools import wraps

VISIT_COOLDOWN_SECONDS = 300    # 5 minutes

app = Flask(__name__)
app.secret_key = secret_key()
db.initiate_database()


def should_increment_visit(target_type, target_id):
    key = f"{target_type}:{target_id}"
    last_page_visits = session.get('last_page_visits', {})
    if not isinstance(last_page_visits, dict):
        last_page_visits = {}

    now = int(time.time())
    last_visit = last_page_visits.get(key)
    if last_visit is None or now - int(last_visit) >= VISIT_COOLDOWN_SECONDS:
        last_page_visits[key] = now
        session['last_page_visits'] = last_page_visits
        return True
    return False


def isAuth(f):
    @wraps(f)
    def wrapper(postid, *args, **kwargs):
        user_id = session.get('userid')
        if not user_id:
            return redirect(url_for('login'))
        if not postid:
            return f(*args, **kwargs)
        try:
            post = db.fetch_post(postid)
        except ValueError:
            return abort(404)

        if post.get('userid') != user_id:
            return abort(403)

        return f(postid, *args, post=post, **kwargs)
    return wrapper


@app.route("/")
def index():
    posts = db.fetch_posts()
    return render_template('index.html', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            db.create_user(username, password)
            return redirect(url_for('success'))
        except sqlite3.IntegrityError:
            flash('Käyttäjänimi on jo käytössä.')
            return redirect(url_for('register'))
    return render_template('register.html')


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', next_page=request.referrer)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next_url = request.form.get('next_page') or url_for('index')

        try:
            result = db.login_user(username, password)
            session['userid'] = result[0]
            session['username'] = result[1]
            return redirect(next_url or url_for('index'))
        except ValueError as e:
            error_message = str(e)
            flash(error_message)
            return redirect(url_for('login'), next_page=next_url)
    return render_template('login.html')


@app.route('/user/<int:userid>')
def user_page(userid: int):
    try:
        posts = db.fetch_userposts(userid)
        user = db.fetch_user(userid)
    except ValueError:
        return abort(404)
    if userid != session.get('userid'):
        if should_increment_visit('user', userid):
            db.increment_page_visits('user', userid)
    stats = db.fetch_page_stats('user', userid)
    liked = False
    if session.get('userid'):
        liked = db.has_user_liked('user', userid, session['userid'])
    return render_template('userpage.html', posts=posts, user=user, stats=stats, liked=liked)


@app.route('/like/user/<int:userid>', methods=['POST'])
def like_user(userid: int):
    user_id = session.get('userid')
    if not user_id:
        return redirect(url_for('login'))
    try:
        db.create_page_like('user', userid, user_id)
    except sqlite3.Error:
        pass  # Already liked or error, just redirect
    return redirect(url_for('user_page', userid=userid))


@app.route('/unlike/user/<int:userid>', methods=['POST'])
def unlike_user(userid: int):
    user_id = session.get('userid')
    if not user_id:
        return redirect(url_for('login'))
    try:
        db.delete_page_like('user', userid, user_id)
    except sqlite3.Error:
        pass
    return redirect(url_for('user_page', userid=userid))


# If a post had a link to this it'd be pretty annoying
@app.route('/logout')
def logout():
    session.pop('userid')
    session.pop('username')
    return redirect(url_for('index'))


@app.route('/create-post', methods=['GET', 'POST'])
def posting_page():
    if not session.get('userid'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        t = request.form['title']
        content = request.form['content']
        try:
            db.create_post(session['userid'], t, content)
            return redirect(url_for('index'))
        except sqlite3.Error:
            flash('Failed to create post. Please try again.')
            return redirect(url_for('posting_page'))
    return render_template('create-post.html')


@app.route('/post/<int:postid>', methods=['GET', 'POST'])
def post_page(postid: int):
    if request.method == 'POST':
        if not session.get('userid'):
            return redirect(url_for('login'))
        comment = request.form['comment']
        try:
            db.create_comment(session['userid'], postid, comment)
        except sqlite3.Error:
            # maybe flash error, for now, just redirect
            pass
        return redirect(url_for('post_page', postid=postid))

    if should_increment_visit('post', postid):
        db.increment_page_visits('post', postid)
    try:
        post = db.fetch_post(postid)
    except ValueError:
        return abort(404)
    comments = db.fetch_comments(postid)
    for comment in comments:
        try:
            comment['username'] = db.fetch_user(comment['userid']).get('username')
        except ValueError:
            comment['username'] = 'Unknown'
    stats = db.fetch_page_stats('post', postid)
    liked = False
    if session.get('userid'):
        liked = db.has_user_liked('post', postid, session['userid'])
    return render_template('post-page.html', post=post, comments=comments, stats=stats, liked=liked)


@app.route('/like/post/<int:postid>', methods=['POST'])
def like_post(postid: int):
    user_id = session.get('userid')
    if not user_id:
        return redirect(url_for('login'))
    try:
        db.create_page_like('post', postid, user_id)
    except sqlite3.Error:
        pass
    return redirect(url_for('post_page', postid=postid))


@app.route('/unlike/post/<int:postid>', methods=['POST'])
def unlike_post(postid: int):
    user_id = session.get('userid')
    if not user_id:
        return redirect(url_for('login'))
    try:
        db.delete_page_like('post', postid, user_id)
    except sqlite3.Error:
        pass
    return redirect(url_for('post_page', postid=postid))


@app.route('/delete-post/<int:postid>', methods=['GET', 'POST'])
@isAuth
def delete_page(postid, post):
    if request.method == 'POST':
        if request.form['action'] == 'Poista':
            try:
                db.delete_post(postid)
                return redirect(url_for('index'))
            except sqlite3.Error:
                return render_template('delete-post.html', post=post, error='Failed to delete post.')
        elif request.form['action'] == 'Palaa takaisin':
            return redirect(url_for('index'))
    return render_template('delete-post.html', post=post)


@app.route('/edit/<int:postid>', methods=['GET', 'POST'])
@isAuth
def edit_page(postid, post):
    if request.method == 'POST':
        update_title = request.form['title']
        updated_desc = request.form['content']
        try:
            db.update_content(update_title, updated_desc, postid)
            return redirect(url_for('post_page', postid=postid))
        except sqlite3.Error:
            return render_template('edit-post.html', post=post, error='Failed to update post.')
    return render_template('edit-post.html', post=post)


@app.route("/search")
def search():
    query = request.args.get("query")
    try:
        results = db.search_post(query) if query else []
    except sqlite3.Error:
        flash('Search failed. Please try again.')
        redirect(url_for('search'))
    return render_template("search.html", query=query, results=results)


@app.route('/test')
def test():
    return render_template('test.html')