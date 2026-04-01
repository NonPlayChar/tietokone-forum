from flask import Flask, request, render_template, redirect, session, abort, url_for
import database as db
from functions import secret_key
from functools import wraps

app = Flask(__name__)
app.secret_key = secret_key()
db.initiate_database()

loggedin_user = None


def isAuth(f):
    @wraps(f)
    def wrapper(postid, *args, **kwargs):
        user_id = session.get('userid')
        if not user_id:
            return redirect(url_for('login', next=request.url))
        if not postid:
            return f(postid, *args, post=post, **kwargs)
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

        return redirect('/success')
    return render_template('register.html')


@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
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
            return redirect('/')
    return render_template('login.html')


@app.route('/user/<int:userid>')
def user_page(userid: int):
    posts = db.fetch_userposts(userid)
    user = db.fetch_user(userid)
    return render_template('userpage.html', posts=posts, user=user)


# If a post had a link to this it'd be pretty annoying
@app.route('/logout')
def logout():
    session.pop('userid')
    session.pop('username')
    return redirect('/')


@app.route('/create-post', methods=['GET', 'POST'])
def posting_page():
    if not session.get('userid'):
        return redirect('/login')
    if request.method == 'POST':
        t = request.form['title']
        content = request.form['content']
        db.create_post(session['userid'], t, content)
        return redirect('/')
    return render_template('create-post.html')


@app.route('/post/<int:postid>')
def post_page(postid: int):
    return render_template('post-page.html', post=db.fetch_post(postid))


@app.route('/delete-post/<int:postid>', methods=['GET', 'POST'])
@isAuth
def delete_page(postid):
    if request.method == 'POST':
        if request.form['action'] == 'Poista':
            delete_post(postid)
            return redirect('/')
        elif request.form['action'] == 'Palaa takaisin':
            return redirect('../')
    return render_template('delete-post.html', post=post)


@app.route("/search")
def search():
    query = request.args.get("query")
    results = db.search_post(query) if query else []
    return render_template("search.html", query=query, results=results)


@app.route('/edit/<int:postid>', methods=['GET', 'POST'])
@isAuth
def edit_page(postid, post):
    if request.method == 'POST':
        updated_desc = request.form['content']
        db.update_content(postid, updated_desc)
        return redirect(url_for('post_page', postid=postid))
    return render_template('edit-post.html', post=post)


@app.route('/test')
def test():
    return render_template('test.html')