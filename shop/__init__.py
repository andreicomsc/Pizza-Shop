from flask import Flask
from shop.key import KEY
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .csrf import csrf


app = Flask(__name__)
app.config["SECRET_KEY"] = KEY
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
csrf.init_app(app)

login_manager.login_view = "login"
login_manager.login_message = "You need to be logged in to access this page."

from . import routes
