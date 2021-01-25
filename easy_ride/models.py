from easy_ride import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from datetime import datetime
import random
import enum

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class CityName(enum.Enum):
    GLASGOW = "Glasgow City"

class UserType(enum.Enum):
    NORMAL = "Normal User"
    OPERATOR = "Operator"
    MANAGER = "Manager"

class PaymentType(enum.Enum):
    CARD = "Credit Card"
    WALLET = "Wallet"

class BikeStatus(enum.Enum):
    YES = "Available"
    NO = "Not Available"

class LocationNames(enum.Enum):
    HILLHEAD = "Hillhead, Glasgow"
    PARTICK = "Partick, Glasgow"
    FINNIESTON = "Finnieston, Glasgow"
    GOVAN = "Govan, Glasgow"
    LAURIESTON = "Laurieston, Glasgow"

class PaidStatus(enum.Enum):
    YES = "Paid"
    NO = "Not Paid"

class User(db.Model,UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True)
    profile_image = db.Column(db.String(64),nullable=False,default='default_profile.jpg')
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    created_at = db.Column(db.DateTime)
    country_code = db.Column(db.Integer, default = '44')
    phone_number = db.Column(db.Integer)
    email = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    city = db.Column(db.Enum(CityName), default = 'GLASGOW')
    user_type = db.Column(db.Enum(UserType))
    wallet = db.Column(db.Float, default=0)

    rides = db.relationship('Transaction',backref='user',lazy=True)
    login_log = db.relationship('LoginLog',backref='user',lazy=True)
    current_ride = db.relationship('StartRide',backref='user',lazy=True)
    ride_log = db.relationship('RideLog',backref='user',lazy=True)

    def __init__(self,first_name, last_name, phone_number, email,password, city, user_type):
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = datetime.utcnow()
        self.phone_number = phone_number
        self.city = city
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.user_type = user_type

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return f"Name {self.first_name} {self.last_name}"

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer,primary_key=True)
    transaction_id = db.Column(db.String(64),unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    payment_type = db.Column(db.Enum(PaymentType))
    credit_card_number = db.Column(db.String(16))
    amount = db.Column(db.Float)
    time = db.Column(db.DateTime)
    ride_id = db.Column(db.String(64),db.ForeignKey('current_rides.ride_id'),unique=True)
    paid = db.Column(db.Enum(PaidStatus))

    def __init__(self, user_id, payment_type, credit_card_number, amount, ride_id, paid):
        self.user_id = user_id
        self.payment_type = payment_type
        self.credit_card_number = credit_card_number
        self.amount = amount
        self.time = datetime.utcnow()
        self.transaction_id = str(user_id) + str(payment_type) + str(self.time)
        self.ride_id = ride_id
        self.paid = paid

class LoginLog(db.Model):
    __tablename__ = 'login_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    logged_at = db.Column(db.DateTime)
    user_type = db.Column(db.Enum(UserType))

    def __init__(self, user_id, user_type, logged_at):
        self.user_id = user_id
        self.user_type = user_type
        self.logged_at = datetime.utcnow()

class BikeInfo(db.Model):
    __tablename__ = 'bike_info'

    id = db.Column(db.Integer, primary_key=True)
    bike_number = db.Column(db.Integer, unique=True,index=True)
    bike_pin = db.Column(db.Integer)
    status = db.Column(db.Enum(BikeStatus))
    last_location = db.Column(db.Enum(LocationNames))

    current_rides = db.relationship('StartRide',backref='bike',lazy=True)
    ride_log = db.relationship('RideLog',backref='bike',lazy=True)

    def __init__(self, bike_number, status, last_location):
        self.bike_number = bike_number
        self.bike_pin = random.randint(1000,9999)
        self.status = status
        self.last_location = last_location

    def check_available(self):
        if self.status == 'YES':
            return True
        else:
            return False

class StartRide(db.Model):
    __tablename__ = 'current_rides'

    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.String(64),unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    bike_number = db.Column(db.Integer, db.ForeignKey('bike_info.bike_number'),nullable=False)
    start_location = db.Column(db.Enum(LocationNames))
    start_time = db.Column(db.DateTime)

    transaction = db.relationship('Transaction',backref='ride',lazy=True)
    ride_log = db.relationship('RideLog',backref='ride',lazy=True)

    def __init__(self, user_id, bike_number, start_location):
        self.user_id = user_id
        self.bike_number = bike_number
        self.start_location = start_location
        self.start_time = datetime.utcnow()
        self.ride_id = str(user_id) + str(bike_number) + str(self.start_time)

class RideLog(db.Model):
    __tablename__ = 'ride_log'

    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.String(64),db.ForeignKey('current_rides.ride_id'),unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    bike_number = db.Column(db.Integer, db.ForeignKey('bike_info.bike_number'),nullable=False)
    start_location = db.Column(db.Enum(LocationNames))
    end_location = db.Column(db.Enum(LocationNames))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __init__(self, ride_id, user_id, bike_number, start_location, end_location, start_time):
        self.ride_id = ride_id
        self.user_id = user_id
        self.bike_number = bike_number
        self.start_location = start_location
        self.end_location = end_location
        self.start_time = start_time
        self.end_time = datetime.utcnow()
