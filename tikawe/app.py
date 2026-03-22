from flask import Flask, request, render_template, redirect, session
from database import initiate_database, create_user, login_user, fetch_user, create_post, fetch_posts, fetch_post
from functions import secret_key

app = Flask(__name__)
app.secret_key = secret_key()
initiate_database()

loggedin_user = None


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
    if not session or not session['userid']:
        return redirect('/login')
    return render_template('userpage.html')



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

@app.route('/test')
def test():
    return render_template('test.html')