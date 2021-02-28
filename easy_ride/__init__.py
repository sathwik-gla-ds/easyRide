# Creates the flask and db object and sets the appropiate configurations

from flask import Flask,flash,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__) # Main flask object imported in app.py
app.config['SECRET_KEY'] = 'mysecret'


#===============================================================#
# MySQL Database Config settings. Database is hosted in AWS RDS #
#===============================================================#
username = 'hd'
password = 'easy_ridehd1503'
endpoint = '182.92.235.32:3306'
database = 'easy_ride'
# config settings required for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{username}:{password}@{endpoint}/{database}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) # creates a database class
Migrate(app,db) # A library used for traking modifications to the database from the app. Not essential but makes it easier.
#===============================================================#


#Login object and configs to handle logins and authentications
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'


#=========================================================================================#
# Blueprints for dividing files into various directories which makes it easier to work on #
#=========================================================================================#
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
#=========================================================================================#
