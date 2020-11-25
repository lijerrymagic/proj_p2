from flask import Flask
import flask_login

login_manager = flask_login.LoginManager()


# from flask_mysqldb import MySQL
#
app = Flask(__name__)
app.secret_key = 'super secret string'
#
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '123456'
# app.config['MYSQL_DB'] = 'proj_p2'
#
# mysql = MySQL(app)
login_manager.init_app(app)
import app_module.views
import app_module.db
import app_module.models