from flask_login import UserMixin
from app_module import login_manager


class User(UserMixin):
    def __init__(self, user_id, user_type):
        self.id = user_id
        self.name = "user " + str(user_id)
        self.password = self.name + "_secret"
        self.user_type = user_type

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


class Vehicle:
    def __init__(self, make, model, year, vin_num, license_num, class_num, location_id, veh_id=None):
        self.make = make
        self.model = model
        self.year = year
        self.vin_num = vin_num
        self.license_num = license_num
        self.class_num = class_num
        self.location_id = location_id
        self.veh_id = veh_id


class Customer:
    def __init__(self, cust_type, first_name, last_name, cust_email, cust_phonenum, address_id, username, password,
                 cust_id=None):
        self.cust_type = cust_type
        self.first_name = first_name
        self.last_name = last_name
        self.cust_email = cust_email
        self.cust_phonenum = cust_phonenum
        self.address_id = address_id
        self.username = username
        self.password = password
        self.cust_id = cust_id


class Address:
    def __init__(self, state, city, street, zipcode, addr_id=None):
        self.state = state
        self.city = city
        self.street = street
        self.zipcode = zipcode
        self.addr_id = addr_id


class Location:
    def __init__(self, phone, state, city, street, zipcode, location_id=None):
        self.phone = phone
        self.state = state
        self.city = city
        self.street = street
        self.zipcode = zipcode
        self.location_id = location_id


class Rental:
    def __init__(self, pickup_date, dropoff_date, start_odometer, end_odometer, daily_limit, cust_id=None,
                 cust_type=None, veh_id=None, ren_pickuplocid=None, ren_dropoffloc_id=None, inv_id=None, cou_id=None,
                 rental_id=None):
        self.pickup_date = pickup_date
        self.dropoff_date = dropoff_date
        self.start_odometer = start_odometer
        self.end_odometer = end_odometer
        self.daily_limit = daily_limit
        self.cust_id = cust_id
        self.cust_type = cust_type
        self.veh_id = veh_id
        self.ren_pickuplocid = ren_pickuplocid
        self.ren_dropoffloc_id = ren_dropoffloc_id
        self.inv_id = inv_id
        self.cou_id = cou_id
        self.rental_id = rental_id


class Coupon:
    def __init__(self, cou_rate, validstart, validend, cou_id=None):
        self.cou_rate = cou_rate
        self.validstart = validstart
        self.validend = validend
        self.cou_id = cou_id


class VehicleClass:
    def __init__(self, vc_name, vc_rateperday, vc_feeovermile, vc_num=None):
        self.vc_name = vc_name
        self.vc_rateperday = vc_rateperday
        self.vc_feeovermile = vc_feeovermile
        self.vc_num = vc_num


class Corporation:
    def __init__(self, corp_name, corp_regnum, corp_id=None):
        self.corp_name = corp_name
        self.corp_regnum = corp_regnum
        self.corp_id = corp_id


class Individual:
    def __init__(self, cust_id, cust_driverlicnum, cust_insurcompname, cust_insurpolnum, cust_type):
        self.cust_id = cust_id
        self.cust_driverlicnum = cust_driverlicnum
        self.cust_insurcompname = cust_insurcompname
        self.cust_insurpolnum = cust_insurpolnum
        self.cust_type = cust_type


class Corporate:
    def __init__(self, cust_id, employee_id, corp_id, cust_type):
        self.cust_id = cust_id
        self.employee_id = employee_id
        self.corp_id = corp_id
        self.cust_type = cust_type


@login_manager.user_loader
def user_loader(cust_id):
    return User(cust_id, "admin")
