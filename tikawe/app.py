from flask import Flask, request, render_template, redirect, session
from database import initiate_database, create_user, login_user, fetch_user
from functions import token

app = Flask(__name__)
app.secret_key = token()
initiate_database()

loggedin_user = None


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        result = create_user(username, password)

        if type(result) == Exception:
            print('Username already in use!')
            return str(result)

        return redirect('/success')
    return render_template('register.html')


@app.route('/success')
def success():
    return "Registration successful!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    print('debug1')
    if request.method == 'POST':
        print('debug2')
        username = request.form['username']
        password = request.form['password']

        result = login_user(username, password)
        if type(result) == ValueError:
            print(str(result))
            error_message = str(result)
            return render_template('login.html', error=error_message)
        if result:
            print('debug3')
            session['userid'] = result[0]
            session['username'] = result[1]
            return redirect('/')
    return render_template('login.html')

@app.route('/user/<int:userid>')
def user_page(userid):
    if session['userid']:
        return render_template('userpage.html')
    return redirect('/login')


@app.route('/logout')
def logout():
    del session['userid']
    del session['username']
    return redirect('/')