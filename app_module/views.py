import smtplib
from email.header import Header
from email.mime.text import MIMEText

from cryptography.fernet import Fernet
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import redirect
from app_module import app
from flask import request, render_template, url_for, session
from app_module import db

from app_module.db import insert_address, insert_customer, insert_vehicle, insert_vehicle_class, insert_office_location, \
    insert_corporation, insert_individual, insert_corporate, get_vehicle_by_id, get_vehicles, get_password, get_user_type, \
    get_all_locations, get_all_vehclasses, get_user_id, get_coupon, get_vehicle_class, get_all_corporations, get_all_vehicles, \
    get_all_customers, delete_corporation, delete_customer, delete_off_loc, delete_veh_class, delete_vehicle, insert_invoice, \
    insert_payment, insert_rental, insert_coupon, insert_cust_coupon
from app_module.models import User, Vehicle, Address, Customer, Rental, VehicleClass, Location, Corporation, Individual, \
    Corporate, Invoice, Payment, Coupon, Cust_coupon

from datetime import date, timedelta

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
            user = User(username, "user")
            login_user(user)
            if username == 'admin':
                return "admin login"
            else:
                return redirect(url_for('index'))
    return 'Bad login'


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template("admin_login.html")
    username = request.form['username']
    password = request.form['password']
    db_password = decrypt(get_password(username))
    if db_password is not None:
        if password == db_password:
            user = User(username, "admin")
            login_user(user)
            return redirect(url_for('manage'))
        else:
            return "wrong password"
    return "username doesn't exist"



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        corporations = get_all_corporations()
        return render_template("register.html", corporations = corporations)
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    cust_type = request.form['cust_type']
    email = request.form['email']
    phone_num = request.form['phone']
    username = request.form['username']
    password = request.form['password']
    state = request.form['state']
    city = request.form['city']
    street = request.form['street']
    zipcode = request.form['zipcode']
    cust_driverlicnum = request.form['cust_driverlicnum']
    cust_insurcompname = request.form['cust_insurcompname']
    cust_insurpolnum = request.form['cust_insurpolnum']
    employee_id = request.form['emp_id']
    corp_id = request.form.get('corporations')

    if cust_type not in ("I", "C"):
        return redirect(url_for("cust_type_msg"))

    encrypted_password = encrypt(password)

    # TODO post save to db
    address_obj = Address(state, city, street, zipcode)
    addr_id = insert_address(address_obj)
    cust_id = insert_customer(
        Customer("I", first_name, last_name, email, phone_num, addr_id, username, encrypted_password))
    if cust_type == "I":
        if cust_driverlicnum =='' or  cust_insurcompname =='' or cust_insurpolnum =='':
            return redirect(url_for("cust_type_msg"), code=303)
        individual_obj = Individual(cust_id, cust_driverlicnum, cust_insurcompname, cust_insurpolnum, cust_type)
        insert_individual(individual_obj)
        # auto add coupon
        coupon_obj = Coupon(5, date.today(), date.today()+timedelta(days=90))
        cou_id = insert_coupon(coupon_obj)
        cust_coupon_obj = Cust_coupon(cou_id, cust_id, cust_type, cust_type)
        insert_cust_coupon(cust_coupon_obj)

    elif cust_type == "C":
        if employee_id =='' or  corp_id =='':
            return redirect(url_for("cust_type_msg"), code=303)
        corporate_obj = Corporate(cust_id, employee_id, corp_id, cust_type)
        insert_corporate(corporate_obj)
        # auto add coupon
        coupon_obj = Coupon(10, date.today(), date.today()+timedelta(days=180))
        cou_id = insert_coupon(coupon_obj)
        cust_coupon_obj = Cust_coupon(cou_id, cust_id, cust_type, cust_type)
        insert_cust_coupon(cust_coupon_obj)

    return redirect(url_for("login"), code=303)





@app.route('/cust_type_msg', methods=['GET'])
def cust_type_msg():
    return render_template("cust_type_msg.html")


@app.route('/corp_register', methods=['GET', 'POST'])
def corp_register():
    if request.method == 'GET':
        return render_template("corporation.html")

    corp_name = request.form['corp_name']
    corp_regnum = request.form['corp_regnum']

    corp_obj = Corporation(corp_name, corp_regnum)
    corp_id = insert_corporation(corp_obj)
    return redirect(url_for("login"), code=303)


@app.route('/manage')
@login_required
def manage():
    return render_template("manage.html")


@app.route('/man_delete', methods=['GET', 'POST'])
@login_required
def man_delete():
    if request.method == 'GET':
        locations = get_all_locations()
        classes  = get_all_vehclasses()
        vehicles = get_all_vehicles()
        customers = get_all_customers()
        corporations = get_all_corporations()
        return render_template("man_delete.html", classes = classes, locations = locations, vehicles = vehicles,
                               customers = customers, corporations = corporations)
    vc_num =  request.form.get('vehicle_class')
    location_id = request.form.get('location')
    veh_id = request.form.get('vehicle')
    cust_id = request.form.get('customer')
    corp_id = request.form.get('corporation')
    delete_veh_class(vc_num)
    delete_off_loc(location_id)
    delete_vehicle(veh_id)
    delete_customer(cust_id)
    delete_corporation(corp_id)

    return redirect(url_for("man_delete"), code=303)


@app.route('/man_veh_class', methods=['GET', 'POST'])
@login_required
def man_veh_class():
    if request.method == 'GET':
        return render_template("man_veh_class.html")
    vc_name = request.form['vc_name']
    vc_rateperday = request.form['vc_rateperday']
    vc_feeovermile = request.form['vc_feeovermile']
    class_obj = VehicleClass(vc_name, vc_rateperday, vc_feeovermile)
    vc_num = insert_vehicle_class(class_obj)
    return redirect(url_for("man_veh_class"), code=303)


@app.route('/man_off_loc', methods=['GET', 'POST'])
@login_required
def man_off_loc():
    if request.method == 'GET':
        return render_template("man_off_loc.html")
    phone = request.form['phone']
    state = request.form['state']
    city = request.form['city']
    street = request.form['street']
    zipcode = request.form['zipcode']
    location_obj = Location(phone, state, city, street, zipcode)
    ol_id = insert_office_location(location_obj)
    return redirect(url_for("man_off_loc"), code=303)


@app.route('/man_vehicles', methods=['GET', 'POST'])
@login_required
def man_vehicles():
    if request.method == 'GET':
        locations = get_all_locations()
        classes  = get_all_vehclasses()
        return render_template("man_vehicles.html", classes=classes, locations=locations)
    make = request.form['make']
    model = request.form['model']
    year = request.form['year']
    vin_num = request.form['vin_num']
    license_num = request.form['license_num']
    class_num = request.form['vehicle_class']
    location_id = request.form['location']
    vehicle_obj = Vehicle(make, model, year, vin_num, license_num, class_num, location_id)
    veh_id = insert_vehicle(vehicle_obj)
    return redirect(url_for("man_vehicles"), code=303)


@app.route('/index')
@login_required
def index():
    vehicles_rs = get_vehicles()
    vehicles = []
    for t in vehicles_rs:
        vehicles.append((Vehicle(t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[0]), get_vehicle_class(t[0])))
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
                        code=302)


@app.route('/vehicles/<string:vehicle_id>/payment', methods=['GET', 'POST'])
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
    coupon = None
    if add_coupon == 'on':
        coupon = get_coupon(cust_id)

    rental_object_partial = Rental(pickup_date, dropoff_date, start_odometer, end_odometer, daily_limit, ren_pickuplocid=pickup_location, ren_dropoffloc_id=dropoff_location,)
    base_payment, overmiles_payment, total_payment, discount = payment_calculate(vehicle_id
                                                                                 , rental_object_partial, coupon)
    if request.method == 'GET':
        return render_template("rent_payment.html", vehicle=vehicle, vehicle_images=vehicle_images
                               , base_payment=base_payment, overmiles_payment=overmiles_payment, discount=discount
                               , total_payment=total_payment, coupon = coupon)

    # creating invoice
    invoice = Invoice(date.today(), total_payment)
    inv_id = insert_invoice(invoice)

    # creating payment
    email_address = request.form.get('email_address')
    pay_method = request.form.get('pay_method')
    card_num = request.form.get('card_num')

    payment = Payment(date.today(), pay_method, int(card_num), inv_id, total_payment)
    insert_payment(payment)

    # create rental
    user_type = get_user_type(cust_name)
    rental = Rental(pickup_date, dropoff_date, start_odometer, end_odometer, daily_limit, cust_id, user_type
                    , vehicle_id, pickup_location, dropoff_location, inv_id, coupon)
    insert_rental(rental)

    # sending digital invoice
    content = "Your rental is from {0} - {1}.\n Total payment is {2}".format(pickup_date, dropoff_date, total_payment)
    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = Header("Digital invoice of your rental")
    msg["From"] = Header("WOW Rental")
    msg["To"] = Header(email_address)

    mailhost = "smtp.gmail.com"
    usermail = "wowrentalcompany@gmail.com"
    password = "Welcome@1"

    try:
        server = smtplib.SMTP(mailhost, 587, timeout=5)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(usermail, password)
        server.sendmail(usermail, [email_address],
                        msg.as_string())
        server.quit()
    except Exception as e:
        print(str(e))
    return redirect(url_for('rent_invoice', vehicle_id=vehicle.veh_id, total_payment=total_payment
                            , email_address=email_address), code=302)


@app.route('/vehicles/<string:vehicle_id>/invoice', methods=['GET'])
@login_required
def rent_invoice(vehicle_id):
    vehicle = get_vehicle_by_id(vehicle_id)
    total_payment = request.args.get('total_payment')
    email_address = request.args.get('email_address')
    return render_template("rent_invoice.html", vehicle=vehicle, vehicle_images=vehicle_images
                           , total_payment=total_payment, email_address=email_address)


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

    pickup_date_list = rental.ren_pickupdate.split('-')
    dropoff_date_list = rental.ren_dropoffdate.split('-')
    pickup_date = date(int(pickup_date_list[0]), int(pickup_date_list[1]), int(pickup_date_list[2]))
    dropoff_date = date(int(dropoff_date_list[0]), int(dropoff_date_list[1]), int(dropoff_date_list[2]))
    days_between = (dropoff_date - pickup_date).days

    # total payment = base payment + overmiles payment + discount
    base_payment = days_between * int(veh_class.vc_rateperday)
    total_limit = days_between * int(rental.ren_dailylimit)
    over_miles = (int(rental.ren_endodometer) - int(rental.ren_startodometer)) - total_limit
    over_miles = 0 if over_miles < 0 else over_miles
    overmiles_payment = over_miles * int(veh_class.vc_feeovermile)


    total_payment = (base_payment + overmiles_payment)
    discount = 0
    if coupon is not None:
        discount = total_payment * int(coupon.cou_rate) / 100
        total_payment = total_payment * (1 - int(coupon.cou_rate) / 100)

    return base_payment, overmiles_payment, total_payment, discount
