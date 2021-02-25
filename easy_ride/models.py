# Defines the classes for database tables, columns and their value types

from easy_ride import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from datetime import datetime
import random
import enum

# Function for loading the current user details to the login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


#=========================================#
# Custom datatypes for some of the columns#
#=========================================#
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
#=========================================#


# User Class for the table users which contains all the user details
class User(db.Model,UserMixin):
    __tablename__ = 'users' # Table name to be mentioned in the database

    # Attributes / Database Columns
    id = db.Column(db.Integer,primary_key=True)
    profile_image = db.Column(db.String(64),nullable=False,default='default_profile.jpg')
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    created_at = db.Column(db.DateTime)
    country_code = db.Column(db.Integer, default = '44')
    phone_number = db.Column(db.Integer)
    email = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    city = db.Column(db.Enum(CityName), default = 'GLASGOW') # GLASGOW
    user_type = db.Column(db.Enum(UserType)) # Whether a normal user or an employee such as operator or manager
    wallet_balance = db.Column(db.Float, default=0)
    session_var = db.Column(db.String(64)) # Used for controlling what options to show to the user in the frontend Navbar
    user_status = db.Column(db.Enum(UserStatus)) # Whether an account is active or disabled

    # relationship with other classes/ database tables
    rides = db.relationship('Transaction',backref='user',lazy=True)
    login_log = db.relationship('LoginLog',backref='user',lazy=True)
    ride_log = db.relationship('RideLog',backref='user',lazy=True)
    reviews = db.relationship('Review',backref='user',lazy=True)
    repairs = db.relationship('Repair',backref='user',lazy=True)

    # For creating a new user object / table record
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
    # For checking the password used while user logs in
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    # For adding/deducting balance to/from the wallet
    def add_wallet_balance(self, balance):
        self.wallet_balance += balance
    def deduct_wallat_balance(self, balance):
        self.wallet_balance -= balance

    def __repr__(self):
        return f"Name {self.first_name} {self.last_name}"


# Transaction Class for the table transactions which contains all the payment records
class Transaction(db.Model):
    __tablename__ = 'transactions' # Table name to be mentioned in the database

    # Attributes / Database Columns
    id = db.Column(db.Integer,primary_key=True)
    transaction_id = db.Column(db.String(64),unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False) #Linked to users table
    payment_type = db.Column(db.Enum(PaymentType)) # CARD, WALLET
    credit_card_number = db.Column(db.String(16))
    amount = db.Column(db.Float)
    time = db.Column(db.DateTime)
    ride_id = db.Column(db.String(64),db.ForeignKey('ride_log.ride_id'),unique=True) #Linked to ridelogs table
    paid = db.Column(db.Enum(PaidStatus)) # YES, NO

    # For creating a new pending payment object / table record
    def __init__(self, user_id, payment_type, amount, ride_id, paid):
        self.user_id = user_id
        self.payment_type = payment_type
        self.amount = amount
        self.transaction_id = str(user_id) + str(payment_type) + str(datetime.utcnow())
        self.ride_id = ride_id
        self.paid = paid
    # For updating the payment details
    def update_payment(self, credit_card_number=''):
        self.credit_card_number = credit_card_number
        self.paid = 'YES'
        self.time = datetime.utcnow()


# Topup Class for the table topup_logs which contains all the wallet topup records
class TopUp(db.Model):
    __tablename__ = 'topup_logs' # Table name to be mentioned in the database

    # Attributes / Database Columns
    id = db.Column(db.Integer,primary_key=True)
    transaction_id = db.Column(db.String(64),unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False) #Linked to users table
    credit_card_number = db.Column(db.String(16))
    amount = db.Column(db.Float)
    time = db.Column(db.DateTime)

    # For creating a new wallet top up object / table record
    def __init__(self, user_id, credit_card_number, amount):
        self.user_id = user_id
        self.credit_card_number = credit_card_number
        self.amount = amount
        self.transaction_id = str(user_id) + str(amount) + str(datetime.utcnow())
        self.time = datetime.utcnow()


# LogingLog Class for the table login_logs which contains all the user login records
class LoginLog(db.Model):
    __tablename__ = 'login_logs' # Table name to be mentioned in the database

    # Attributes / Database Columns
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False) #Linked to users table
    logged_at = db.Column(db.DateTime)
    user_type = db.Column(db.Enum(UserType)) #NORMAL, OPERATOR, MANAGER

    # For creating a new login log object / table record
    def __init__(self, user_id, user_type):
        self.user_id = user_id
        self.user_type = user_type
        self.logged_at = datetime.utcnow()


# BikeInfo Class for the table bike_info which contains all the bike records
class BikeInfo(db.Model):
    __tablename__ = 'bike_info' # Table name to be mentioned in the database

    # Attributes / Database Columns
    id = db.Column(db.Integer, primary_key=True)
    bike_number = db.Column(db.Integer, unique=True,index=True)
    bike_pin = db.Column(db.Integer)
    status = db.Column(db.Enum(BikeStatus)) # YES, NO, REPAIR, DISABLED
    last_location = db.Column(db.Enum(LocationNames)) # HILLHEAD, PARTICK, FINNIESTON, GOVAN, LAURIESTON

    # relationship with other classes/ database tables
    ride_log = db.relationship('RideLog',backref='bike',lazy=True)

    # For creating a new bike object / table record
    def __init__(self, bike_number, status, last_location):
        self.bike_number = bike_number
        self.bike_pin = random.randint(1000,9999)
        self.status = status
        self.last_location = last_location
    # To check if a bike is available
    def check_available(self):
        if self.status == 'YES':
            return True
        else:
            return False
    # To ruturn a bike after a ride
    def place_back(self, loaction):
        self.bike_pin = random.randint(1000,9999) # Change the bike pin to new random number
        self.last_location = loaction # Update the location to where it is being returned
        self.status = 'YES' # Update the status to available


# RideLog Class for the table ride_logs which contains all the ride log records
class RideLog(db.Model):
    __tablename__ = 'ride_log' # Table name to be mentioned in the database

    # Attributes / Database Columns
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.String(64),unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False) #Linked to users table
    bike_number = db.Column(db.Integer, db.ForeignKey('bike_info.bike_number'),nullable=False) #Linked to bikeinfo table
    start_location = db.Column(db.Enum(LocationNames)) # HILLHEAD, PARTICK, FINNIESTON, GOVAN, LAURIESTON
    end_location = db.Column(db.Enum(LocationNames))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    current =  db.Column(db.Enum(CurrentStatus)) # YES, NO

    # relationship with other classes/ database tables
    transaction = db.relationship('Transaction',backref='ride',lazy=True)

    # For creating a new ride log object / table record
    def __init__(self, user_id, bike_number, start_location, current):
        self.user_id = user_id
        self.bike_number = bike_number
        self.start_location = start_location
        self.start_time = datetime.utcnow()
        self.ride_id = str(user_id) + str(bike_number) + str(self.start_time)
        self.current = current
    # Get the duration of the ride
    def get_minutes(self, end_time):
        time_delta = (end_time - self.start_time)
        total_seconds = time_delta.total_seconds()
        return 1 + int(total_seconds/60)
    # Update the ride details at end of the ride
    def end_ride(self, end_location):
        self.end_location = end_location
        self.end_time = datetime.utcnow()
        self.current = 'NO'


# Review Class for the table reviews which contains all the user ratings and review records
class Review(db.Model):
    __tablename__ = 'reviews' # Table name to be mentioned in the database

    # Attributes / Database Columns
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False) #Linked to users table
    ride_id = db.Column(db.String(64),db.ForeignKey('ride_log.ride_id'), unique=True) #Linked to ridelog table
    reviewed_at = db.Column(db.DateTime)
    rating = db.Column(db.Integer) #1,2,3,4,5
    review = db.Column(db.Text)

    # For creating a new review object / table record
    def __init__(self, user_id, ride_id, rating, review):
        self.user_id = user_id
        self.ride_id = ride_id
        self.rating = rating
        self.review = review
        self.reviewed_at = datetime.utcnow()


# Repair Class for the table repairs which contains all the user reports and operator repair records
class Repair(db.Model):
    __tablename__ = 'repairs' # Table name to be mentioned in the database

    # Attributes / Database Columns
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False) #Linked to users table
    bike_number = db.Column(db.Integer, db.ForeignKey('bike_info.bike_number'),nullable=False) #Linked to biekinfo table
    created_at = db.Column(db.DateTime)
    description = db.Column(db.Text)
    urgency = db.Column(db.Enum(RepairUrgency)) #LOW, MEDIUM, HIGH
    repair_status =  db.Column(db.Enum(RepairStatus)) # YES, NO
    operator_id = db.Column(db.Integer)
    repaired_at = db.Column(db.DateTime)
    level_of_repair = db.Column(db.Integer) #1,2,3,4,5
    comment = db.Column(db.Text)

    # For creating a new defective bike user report object / table record
    def __init__(self, user_id, bike_number, description, urgency):
        self.user_id = user_id
        self.bike_number = bike_number
        self.description = description
        self.urgency = urgency
        self.created_at = datetime.utcnow()
        self.repair_status = 'NO'
    # For updating the records with operator repair details
    def repaired(self, operator_id, level_of_repair, comment):
        self.operator_id = operator_id
        self.level_of_repair = level_of_repair
        self.comment = comment
        self.repair_status = 'YES'
        self.repaired_at = datetime.utcnow()
