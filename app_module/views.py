from cryptography.fernet import Fernet
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import redirect
from app_module import app
from flask import request, render_template, url_for
from app_module import db
from app_module.db import insert_address, insert_customer, get_vehicle_by_id, get_vehicles, get_password, get_user_type
from app_module.models import User, Vehicle, Address, Customer

vehicle_images = {
    "BMW_M4": "https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/2021-bmw-x5-mmp-1-1600284201.jpg?crop=1xw:0"
           ".84375xh;center,top&resize=480:* ",
    "AUDI_S5": "https://media.ed.edmunds-media.com/audi/s5/2015/oem/2015_audi_s5_convertible_prestige-quattro_fq_oem_1_815.jpg"
}

app_secret = b'YdEadWnAevr_kqP6eTyGOQVjhAw3R0O1RnYLKFde9mU='


@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    username = request.form['username']
    password = request.form['password']
    db_password = decrypt(get_password(username))
    if db_password is not None:
        if password == db_password:
            if get_user_type(username) == "I":
                user = User(username, "user")
            else:
                user = User(username, "admin")
            user.id = username
            login_user(user)
            if user.user_type == "user":
                return redirect(url_for('index'))
            else:
                return "admin login"
    return 'Bad login'


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    email = request.form['email']
    phone_num = request.form['phone']
    username = request.form['username']
    password = request.form['password']
    state = request.form['state']
    city = request.form['city']
    street = request.form['street']
    zipcode = request.form['zipcode']

    encrypted_password = encrypt(password)

    # TODO post save to db
    address_obj = Address(state, city, street, zipcode)
    addr_id = insert_address(address_obj)
    cust_id = insert_customer(Customer("I", first_name, last_name, email, phone_num, addr_id, username, encrypted_password))
    return redirect(url_for("login"), code=303)


@app.route('/index')
@login_required
def index():
    vehicles_rs = get_vehicles()
    vehicles = []
    for t in vehicles_rs:
        vehicles.append(Vehicle(t[0], t[1]))
    return render_template("index.html", vehicles=vehicles, vehicle_images=vehicle_images)


@app.route('/vehicles/<string:vehicle_id>', methods=['GET', 'POST'])
@login_required
def vehicle_page(vehicle_id):
    vehicle_rs = get_vehicle_by_id(vehicle_id)
    if vehicle_rs is not None:
        vehicle = Vehicle(vehicle_rs[0][0], vehicle_rs[0][1])
    if request.method == 'GET':
        return render_template("vehicle_page.html", vehicle=vehicle, vehicle_images=vehicle_images)
    else:
        pickup_date = request.form.get('pickup_date')
        dropoff_date = request.form.get('dropoff_date')
        return redirect(url_for("rent_payment", vehicle_id=vehicle_id), code=303)


@app.route('/vehicles/<string:vehicle_id>/payment', methods=['GET'])
@login_required
def rent_payment(vehicle_id):
    vehicle_rs = get_vehicle_by_id(vehicle_id)
    if vehicle_rs is not None:
        vehicle = Vehicle(vehicle_rs[0][0], vehicle_rs[0][1])
    return render_template("rent_payment.html", vehicle=vehicle, vehicle_images=vehicle_images)


@app.route('/vehicles/<string:vehicle_id>/invoice', methods=['GET'])
@login_required
def rent_invoice(vehicle_id):
    vehicle_rs = get_vehicle_by_id(vehicle_id)
    if vehicle_rs is not None:
        vehicle = Vehicle(vehicle_rs[0][0], vehicle_rs[0][1])
    return render_template("rent_invoice.html", vehicle=vehicle, vehicle_images=vehicle_images)


def encrypt(string):
    """
    Encrypts an encrypted string
    """
    string_encoded = string.encode()
    f = Fernet(load_key())
    string_encrypted = f.encrypt(string_encoded)
    return string_encrypted


def decrypt(string_encrypted):
    """
    Decrypts an encrypted string
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(string_encrypted)
    return decrypted_message.decode()


def load_key():
    return app_secret
