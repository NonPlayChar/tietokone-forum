from flask import Flask, request, render_template, redirect
from database import initiate_database, create_user

app = Flask(__name__)

initiate_database()

loggedin_user = int()

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

@app.route('/user/<int:userid>')
def user_page(userid):
    pass