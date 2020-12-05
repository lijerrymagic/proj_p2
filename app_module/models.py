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


@login_manager.user_loader
def user_loader(cust_id):
    return User(cust_id, "admin")
