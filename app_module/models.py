from flask_login import UserMixin
from app_module import login_manager


class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "user " + str(id)
        self.password = self.name + "_secret"

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


class Vehicle:
    def __init__(self, name, model):
        self.name = name
        self.model = model


@login_manager.user_loader
def user_loader(cust_id):
    return User(cust_id)
