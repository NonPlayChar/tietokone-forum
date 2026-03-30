from flask import Flask, request, render_template, redirect, session, abort
from database import initiate_database, create_user, login_user, fetch_user, create_post, fetch_posts, fetch_post, fetch_userpost, delete_post, search_post, update_content
from functions import secret_key

app = Flask(__name__)
app.secret_key = secret_key()
initiate_database()

loggedin_user = None

def isAuth():
    # A function to check if the session is set and redirect if not
    pass

@app.route("/")
def index():
    posts = fetch_posts()
    return render_template('index.html', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        result = create_user(username, password)

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

        result = login_user(username, password)
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
    posts = fetch_userpost(userid)
    return render_template('userpage.html', posts=posts)



@app.route('/logout')
def logout():
    del session['userid']
    del session['username']
    return redirect('/')

@app.route('/create-post', methods=['GET', 'POST'])
def posting_page():
    if not session or not session['userid']:
        return redirect('/login')
    if request.method == 'POST':
        t = request.form['title']
        cpu = request.form['cpu']
        ram = request.form['ram']
        gpu = request.form['gpu']
        mbd = request.form['mbd']
        storage = request.form['storage']
        desc = request.form['desc']
        create_post(session['userid'], t, cpu, ram, gpu, mbd, storage, desc)
        return redirect('/')
    return render_template('create-post.html')

@app.route('/post/<int:postid>')
def post_page(postid: int):
    return render_template('post-page.html', post=fetch_post(postid))

@app.route('/delete-post/<int:postid>', methods=['GET', 'POST'])
def delete_page(postid):
    if not session or not session['userid']:
        return redirect('/login')
    post = fetch_post(postid)
    post_author_id = post['userid']
    if session['userid'] != post_author_id:
        abort(403)
    if request.method == 'POST':
        if request.form['action'] == 'Poista':
            delete_post(postid)
            return redirect('/')
        elif request.form['action'] == 'Palaa takaisin':
            return redirect('/')
    return render_template('delete-post.html', post=post)

@app.route("/search")
def search():
    query = request.args.get("query")
    results = search_post(query) if query else []
    print(results)
    return render_template("search.html", query=query, results=results)

@app.route('/edit/<int:postid>', methods=['GET', 'POST'])
def edit_page(postid):
    if not session or not session['userid']:
        return redirect('/login')
    post = fetch_post(postid)
    post_author_id = post['userid']
    if session['userid'] != post_author_id:
        abort(403)
    if request.method == 'POST':
        updated_desc = request.form['content']
        print(update_content(updated_desc, postid))
        return redirect(f'../post/{postid}')
    return render_template('edit-post.html', post=post)


@app.route('/test')
def test():
    return render_template('test.html')