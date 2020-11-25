from flask import Flask
import flask_login

login_manager = flask_login.LoginManager()

app = Flask(__name__)
app.secret_key = 'super secret string'

login_manager.init_app(app)

import app_module.views
import app_module.db
import app_module.models
