from cryptography.fernet import Fernet
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import redirect
from app_module import app
from flask import request, render_template, url_for, session
from app_module import db
from app_module.db import insert_address, insert_customer, get_vehicle_by_id, get_vehicles, get_password, get_user_type, \
    get_all_locations, get_user_id, get_coupon, get_vehicle_class
from app_module.models import User, Vehicle, Address, Customer, Rental
from datetime import date

vehicle_images = {
    "BMW_M4": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/2015_BMW_M4_%28F82%29_coupe_%2824220553394%29"
              ".jpg/1200px-2015_BMW_M4_%28F82%29_coupe_%2824220553394%29.jpg",
    "AUDI_S5": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/2018_Audi_S5_TFSi_Quattro_Automatic_3.0"
               "_Front.jpg/1200px-2018_Audi_S5_TFSi_Quattro_Automatic_3.0_Front.jpg",
    "BMW_Z4": "https://upload.wikimedia.org/wikipedia/commons/5/5d/2011_BMW_Z4_sDrive23i_M_Sport_Highline_2.5.jpg",
    "BENZ_GLK": "https://smartcdn.prod.postmedia.digital/driving/images?url=http://smartcdn.prod.postmedia.digital"
                "/driving/wp-content/uploads/2013/08/44582391.jpg&w=580&h=370",
    "BENZ_S63": "https://www.automobilemag.com/uploads/sites/11/2012/02/2012-mercedes-benz-S63-AMG-"
                "front-left-view1.jpg",
    "AUDI_A6": "https://images.wheels.ca/wp-content/uploads/2018/05/Audi-A6-2019-main.jpg"
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
    cust_id = insert_customer(
        Customer("I", first_name, last_name, email, phone_num, addr_id, username, encrypted_password))
    return redirect(url_for("login"), code=303)


@app.route('/index')
@login_required
def index():
    vehicles_rs = get_vehicles()
    vehicles = []
    for t in vehicles_rs:
        vehicles.append(Vehicle(t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[0]))
    return render_template("index.html", vehicles=vehicles, vehicle_images=vehicle_images)


@app.route('/vehicles/<string:vehicle_id>', methods=['GET', 'POST'])
@login_required
def vehicle_page(vehicle_id):
    vehicle = get_vehicle_by_id(vehicle_id)
    if request.method == 'GET':
        locations = get_all_locations()
        locations2 = get_all_locations()
        return render_template("vehicle_page.html", vehicle=vehicle, vehicle_images=vehicle_images,
                               locations=locations, locations2=locations2)
    else:
        pickup_date = request.form.get('pickup_date')
        dropoff_date = request.form.get('dropoff_date')
        pickup_location = request.form.get('pickup_location')
        dropoff_location = request.form.get('dropoff_location')
        start_odometer = request.form.get('start_odometer')
        end_odometer = request.form.get('end_odometer')
        daily_limit = request.form.get('daily_limit')
        add_coupon = request.form.get('add_coupon')

        return redirect(url_for("rent_payment", vehicle_id=vehicle_id, pickup_date=pickup_date
                                , dropoff_date=dropoff_date, pickup_location=pickup_location
                                , dropoff_location=dropoff_location, start_odometer=start_odometer
                                , end_odometer=end_odometer, daily_limit=daily_limit, add_coupon=add_coupon),
                        code=303)


@app.route('/vehicles/<string:vehicle_id>/payment', methods=['GET'])
@login_required
def rent_payment(vehicle_id):
    vehicle = get_vehicle_by_id(vehicle_id)
    pickup_date = request.args.get('pickup_date')
    dropoff_date = request.args.get('dropoff_date')
    pickup_location = request.args.get('pickup_location')
    dropoff_location = request.args.get('dropoff_location')
    start_odometer = request.args.get('start_odometer')
    end_odometer = request.args.get('end_odometer')
    daily_limit = request.args.get('daily_limit')
    add_coupon = request.args.get('add_coupon')

    cust_name = current_user.id
    cust_id = get_user_id(cust_name)
    if add_coupon == 'on':
        coupon = get_coupon(cust_id)

    rental_object_partial = Rental(pickup_date, dropoff_date, pickup_location, dropoff_location,
                                   start_odometer, end_odometer, daily_limit)
    base_payment, overmiles_payment, total_payment, discount = payment_calculate(vehicle_id
                                                                                 , rental_object_partial, coupon)
    return render_template("rent_payment.html", vehicle=vehicle, vehicle_images=vehicle_images
                           , base_payment=base_payment, overmiles_payment=overmiles_payment, discount=discount
                           , total_payment=total_payment)


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


def payment_calculate(vehicle_id, rental, coupon):
    veh_class = get_vehicle_class(vehicle_id)

    pickup_date_list = rental.pickup_date.split('-')
    dropoff_date_list = rental.dropoff_date.split('-')
    pickup_date = date(int(pickup_date_list[0]), int(pickup_date_list[1]), int(pickup_date_list[2]))
    dropoff_date = date(int(dropoff_date_list[0]), int(dropoff_date_list[1]), int(dropoff_date_list[2]))
    days_between = (dropoff_date - pickup_date).days

    # total payment = base payment + overmiles payment + discount
    base_payment = days_between * int(veh_class.vc_rateperday)
    total_limit = days_between * int(rental.daily_limit)
    over_miles = (int(rental.end_odometer) - int(rental.start_odometer)) - total_limit
    over_miles = 0 if over_miles < 0 else over_miles
    overmiles_payment = over_miles * int(veh_class.vc_feeovermile)

    total_payment = (base_payment + overmiles_payment)
    discount = 0
    if coupon is not None:
        discount = total_payment * int(coupon.cou_rate) / 100
        total_payment = total_payment * (1 - int(coupon.cou_rate) / 100)

    return base_payment, overmiles_payment, total_payment, discount
