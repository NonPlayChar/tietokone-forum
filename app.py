import time
from flask import Flask, request, render_template, redirect, session, abort, url_for
import database as db
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
        post = db.fetch_post(postid)
        if not post:
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

        result = db.create_user(username, password)

        if type(result) == Exception:
            print('Username already in use!')
            error_message = str(result)
            return render_template('register.html', error=error_message)

        return redirect(url_for('success'))
    return render_template('register.html')


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        result = db.login_user(username, password)
        if type(result) == ValueError:
            print(str(result))
            error_message = str(result)
            return render_template('login.html', error=error_message)
        if result:
            session['userid'] = result[0]
            session['username'] = result[1]
            return redirect(next_url or url_for('index'))
    return render_template('login.html')


@app.route('/user/<int:userid>')
def user_page(userid: int):
    posts = db.fetch_userposts(userid)
    user = db.fetch_user(userid)
    if should_increment_visit('user', userid):
        db.increment_page_visits('user', userid)
    stats = db.fetch_page_stats('user', userid)
    return render_template('userpage.html', posts=posts, user=user, stats=stats)


@app.route('/like/user/<int:userid>', methods=['POST'])
def like_user(userid: int):
    db.increment_page_likes('user', userid)
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
        db.create_post(session['userid'], t, content)
        return redirect(url_for('index'))
    return render_template('create-post.html')


@app.route('/post/<int:postid>', methods=['GET', 'POST'])
def post_page(postid: int):
    if request.method == 'POST':
        if not session.get('userid'):
            return redirect(url_for('login'))
        comment = request.form['comment']
        db.create_comment(session['userid'], postid, comment)
        return redirect(url_for('post_page', postid=postid))

    if should_increment_visit('post', postid):
        db.increment_page_visits('post', postid)
    post = db.fetch_post(postid)
    comments = db.fetch_comments(postid)
    for comment in comments:
        comment['username'] = db.fetch_user(comment['userid']).get('username')
    stats = db.fetch_page_stats('post', postid)
    return render_template('post-page.html', post=post, comments=comments, stats=stats)


@app.route('/like/post/<int:postid>', methods=['POST'])
def like_post(postid: int):
    db.increment_page_likes('post', postid)
    return redirect(url_for('post_page', postid=postid))


@app.route('/delete-post/<int:postid>', methods=['GET', 'POST'])
@isAuth
def delete_page(postid, post):
    if request.method == 'POST':
        if request.form['action'] == 'Poista':
            db.delete_post(postid)
            return redirect(url_for('index'))
        elif request.form['action'] == 'Palaa takaisin':
            return redirect(url_for('index'))
    return render_template('delete-post.html', post=post)


@app.route('/edit/<int:postid>', methods=['GET', 'POST'])
@isAuth
def edit_page(postid, post):
    if request.method == 'POST':
        updated_desc = request.form['content']
        db.update_content(updated_desc, postid)
        return redirect(url_for('post_page', postid=postid))
    return render_template('edit-post.html', post=post)


@app.route("/search")
def search():
    query = request.args.get("query")
    results = db.search_post(query) if query else []
    return render_template("search.html", query=query, results=results)


@app.route('/test')
def test():
    return render_template('test.html')