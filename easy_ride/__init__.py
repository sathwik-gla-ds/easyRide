#Easy_ride_main/__init__.py

from flask import Flask,flash,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecret'
#Database SETUP
username = 'admin'
password = 'lab02g2c'
endpoint = 'group-project-psd.clsvl0h7k6t3.eu-west-2.rds.amazonaws.com:3306'
database = 'easy_ride'

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{username}:{password}@{endpoint}/{database}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)

#Login configs
login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = 'users.login'

#Blueprints
from easy_ride.core.views import core
from easy_ride.error_pages.handlers import error_pages
from easy_ride.users.views import users
from easy_ride.rides.views import rides
from easy_ride.employees.views import employees

app.register_blueprint(core)
app.register_blueprint(error_pages)
app.register_blueprint(users)
app.register_blueprint(rides)
app.register_blueprint(employees)
