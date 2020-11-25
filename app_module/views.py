from flask_login import login_user, login_required, current_user
from werkzeug.utils import redirect
from app_module import app
from flask import request, render_template, url_for
from app_module import db
from app_module.models import User


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    username = request.form['username']
    password = request.form['password']
    db_password = get_password(username)
    if db_password is not None:
        if password == db_password:
            user = User(username)
            user.id = username
            login_user(user)
            return redirect(url_for('index'))
    return 'Bad login'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    # TODO post save to db
    return 'Bad register'


@app.route('/index')
@login_required
def index():
    return render_template("index.html")


def get_password(username):
    rs = db.run_query('''select password from myusers2 where username = %s''', (username,))
    return rs[0][0] if rs is not None else rs
