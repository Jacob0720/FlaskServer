import csv
import python_utils
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

## SQL DATA BASE GETS INSERTED HERE
## app.config["SQL DATABASE GOES HERE"] = " "

login_manager = LoginManager(app)
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, id):
        self.id = id


def load_users():
    users = {}
    with open('users.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            users[row['username']] = row['password']
    return users


users = load_users()

def user_loader(self, callback):
    self._user_callback = callback
    return self._user_callback

def request_loader(self, callback):
    self._request_callback = callback
    return self._request_callback


def load_user(user_id):
    return User.get(int(user_id))


@app.route('/')
def home():
    ## THIS WILL BE THE HOME TEMPLATE OF HTML PAGE
    return "WELCOME TO AIRES TESTING HOME PAGE"
    ##return render_template('home.html')


@app.route('/<login>', methods=['GET', 'POST'])
def login(login):
    if request.method == 'POST':
        user_id = request.form['username']
        password = request.form['password']

        if user_id in users and password == users[user_id]:
            user = User(user_id)
            login_user(user)
            return redirect(url_for('profile'))
        else:
            return 'Login Failed'

    return "LOGIN FUNCTIONS TO BE IMPLEMENTED"
    ##return render_template('login.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
