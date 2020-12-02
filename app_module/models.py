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
    def __init__(self, name, model):
        self.name = name
        self.model = model


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


@login_manager.user_loader
def user_loader(cust_id):
    return User(cust_id, "admin")
