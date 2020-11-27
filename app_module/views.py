from flask_login import login_user, login_required, current_user
from werkzeug.utils import redirect
from app_module import app
from flask import request, render_template, url_for
from app_module import db
from app_module.models import User, Vehicle

vehicle_images = {
    "bmw": "https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/2021-bmw-x5-mmp-1-1600284201.jpg?crop=1xw:0"
           ".84375xh;center,top&resize=480:* ",
    "audi": "https://media.ed.edmunds-media.com/audi/s5/2015/oem/2015_audi_s5_convertible_prestige-quattro_fq_oem_1_815.jpg"
}


@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
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
    vehicles_rs = get_vehicles()
    vehicles = []
    for t in vehicles_rs:
        vehicles.append(Vehicle(t[0], t[1]))
    return render_template("index.html", vehicles=vehicles, vehicle_images=vehicle_images)


@app.route('/vehicles/<string:vehicle_id>')
def vehicle_page(vehicle_id):
    vehicle_rs = get_vehicle_by_id(vehicle_id)
    if vehicle_rs is not None:
        vehicle = Vehicle(vehicle_rs[0][0], vehicle_rs[0][1])
    return render_template("vehicle_page.html", vehicle=vehicle, vehicle_images=vehicle_images)


def get_password(username):
    rs = db.run_query('''select password from myusers2 where username = %s''', (username,))
    return rs[0][0] if rs is not None else rs


def get_vehicles():
    rs = db.run_query('''select * from vehicle''')
    return rs


def get_vehicle_by_id(vehicle_id):
    rs = db.run_query('''select * from vehicle where name=%s''', (vehicle_id,))
    return rs if rs is not None else rs
