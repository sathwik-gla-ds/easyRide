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
    REPAIR = "In repair"
    DISABLED = "No longer in service"

class LocationNames(enum.Enum):
    HILLHEAD = "Hillhead, Glasgow"
    PARTICK = "Partick, Glasgow"
    FINNIESTON = "Finnieston, Glasgow"
    GOVAN = "Govan, Glasgow"
    LAURIESTON = "Laurieston, Glasgow"

class PaidStatus(enum.Enum):
    YES = "Paid"
    NO = "Not Paid"

class RepairStatus(enum.Enum):
    YES = "Repaired"
    NO = "Not Repaired"

class CurrentStatus(enum.Enum):
    YES = "Ride On Going"
    NO = "Ride Ended"

class UserStatus(enum.Enum):
    NORMAL = "Active account"
    BANNED = "Banned account"
    DELETED = "Account deleted"

class RepairUrgency(enum.Enum):
    LOW = "Small repair"
    MEDIUM = "Medium repair"
    HIGH = "High Priority"


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
    wallet_balance = db.Column(db.Float, default=0)
    session_var = db.Column(db.String(64))
    user_status = db.Column(db.Enum(UserStatus))

    rides = db.relationship('Transaction',backref='user',lazy=True)
    login_log = db.relationship('LoginLog',backref='user',lazy=True)
    ride_log = db.relationship('RideLog',backref='user',lazy=True)
    reviews = db.relationship('Review',backref='user',lazy=True)
    repairs = db.relationship('Repair',backref='user',lazy=True)

    def __init__(self,first_name, last_name, phone_number, email,password, city, user_type):
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = datetime.utcnow()
        self.phone_number = phone_number
        self.city = city
        self.email = email.lower()
        self.password_hash = generate_password_hash(password)
        self.user_type = user_type
        self.user_status = 'NORMAL'

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def add_wallet_balance(self, balance):
        self.wallet_balance += balance

    def deduct_wallat_balance(self, balance):
        self.wallet_balance -= balance

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
    ride_id = db.Column(db.String(64),db.ForeignKey('ride_log.ride_id'),unique=True)
    paid = db.Column(db.Enum(PaidStatus))

    def __init__(self, user_id, payment_type, amount, ride_id, paid):
        self.user_id = user_id
        self.payment_type = payment_type
        self.amount = amount
        self.transaction_id = str(user_id) + str(payment_type) + str(datetime.utcnow())
        self.ride_id = ride_id
        self.paid = paid

    def update_payment(self, credit_card_number=''):
        self.credit_card_number = credit_card_number
        self.paid = 'YES'
        self.time = datetime.utcnow()

class TopUp(db.Model):
    __tablename__ = 'topup_logs'

    id = db.Column(db.Integer,primary_key=True)
    transaction_id = db.Column(db.String(64),unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    credit_card_number = db.Column(db.String(16))
    amount = db.Column(db.Float)
    time = db.Column(db.DateTime)

    def __init__(self, user_id, credit_card_number, amount):
        self.user_id = user_id
        self.credit_card_number = credit_card_number
        self.amount = amount
        self.transaction_id = str(user_id) + str(amount) + str(datetime.utcnow())
        self.time = datetime.utcnow()


class LoginLog(db.Model):
    __tablename__ = 'login_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    logged_at = db.Column(db.DateTime)
    user_type = db.Column(db.Enum(UserType))

    def __init__(self, user_id, user_type):
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

    def place_back(self, loaction):
        self.bike_pin = random.randint(1000,9999)
        self.last_location = loaction
        self.status = 'YES'


class RideLog(db.Model):
    __tablename__ = 'ride_log'

    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.String(64),unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    bike_number = db.Column(db.Integer, db.ForeignKey('bike_info.bike_number'),nullable=False)
    start_location = db.Column(db.Enum(LocationNames))
    end_location = db.Column(db.Enum(LocationNames))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    current =  db.Column(db.Enum(CurrentStatus))

    transaction = db.relationship('Transaction',backref='ride',lazy=True)

    def __init__(self, user_id, bike_number, start_location, current):
        self.user_id = user_id
        self.bike_number = bike_number
        self.start_location = start_location
        self.start_time = datetime.utcnow()
        self.ride_id = str(user_id) + str(bike_number) + str(self.start_time)
        self.current = current

    def get_minutes(self, end_time):
        time_delta = (end_time - self.start_time)
        total_seconds = time_delta.total_seconds()
        return 1 + int(total_seconds/60)

    def end_ride(self, end_location):
        self.end_location = end_location
        self.end_time = datetime.utcnow()
        self.current = 'NO'

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    ride_id = db.Column(db.String(64),db.ForeignKey('ride_log.ride_id'), unique=True)
    reviewed_at = db.Column(db.DateTime)
    rating = db.Column(db.Integer)
    review = db.Column(db.Text)

    def __init__(self, user_id, ride_id, rating, review):
        self.user_id = user_id
        self.ride_id = ride_id
        self.rating = rating
        self.review = review
        self.reviewed_at = datetime.utcnow()

class Repair(db.Model):
    __tablename__ = 'repairs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    bike_number = db.Column(db.Integer, db.ForeignKey('bike_info.bike_number'),nullable=False)
    created_at = db.Column(db.DateTime)
    description = db.Column(db.Text)
    urgency = db.Column(db.Enum(RepairUrgency))
    repair_status =  db.Column(db.Enum(RepairStatus))
    operator_id = db.Column(db.Integer)
    repaired_at = db.Column(db.DateTime)
    level_of_repair = db.Column(db.Integer)
    comment = db.Column(db.Text)

    def __init__(self, user_id, bike_number, description, urgency):
        self.user_id = user_id
        self.bike_number = bike_number
        self.description = description
        self.urgency = urgency
        self.created_at = datetime.utcnow()
        self.repair_status = 'NO'

    def repaired(self, operator_id, level_of_repair, comment):
        self.operator_id = operator_id
        self.level_of_repair = level_of_repair
        self.comment = comment
        self.repair_status = 'YES'
        self.repaired_at = datetime.utcnow()
