from datetime import datetime
import random
from flask import Flask,flash,redirect
from flask_sqlalchemy import SQLAlchemy
from easy_ride.models import User, LoginLog, RideLog, Transaction, Review, Repair, BikeInfo, TopUp
from easy_ride import db
from easy_ride.helpers import format_categories, Cnv2Obj


def repair_bike(form, current_user):
    repair = Repair.query.filter_by(bike_number=form.bike_number, repair_status='NO').first()
    repair.repaired(current_user.id, form.level_of_repair, form.comment)
    bike = BikeInfo.query.filter_by(bike_number=repair.bike_number).first()
    bike.status = 'YES'
    db.session.add_all([repair, bike])
    db.session.commit()
    print('OPERATOR: repaired', form.__dict__)


def move_bike(form):
    bike = BikeInfo.query.filter_by(bike_number=form.bike_number).first()
    bike.place_back(form.new_location)
    db.session.add(bike)
    db.session.commit()
    print('OPERATOR: moved', form.__dict__)


def register_user(form):
    user = User(first_name=form.first_name,
                last_name=form.last_name,
                phone_number=form.phone_number,
                email=form.email,
                password=form.password,
                city=form.city,
                user_type='NORMAL')
    db.session.add(user)
    db.session.commit()


def login_user(form, current_user):
    login_log = LoginLog(current_user.id, current_user.user_type.name)
    db.session.add(login_log)
    db.session.commit()
    print('Logged In', form.__dict__)


def rent_bike(form, current_user):
    current_rides = RideLog.query.filter_by(user_id = current_user.id, current = 'YES').first()
    payment = Transaction.query.filter_by(user_id = current_user.id, paid = 'NO').first()
    if payment is None:
        if current_rides is None:
            bike = BikeInfo.query.filter_by(last_location=form.location, status='YES').first()
            if bike is not None:
                ride = RideLog(user_id = current_user.id,
                                 bike_number = bike.bike_number,
                                 start_location = form.location,
                                 current = "YES")

                bike.status = 'NO'
                user = User.query.filter_by(id=current_user.id).first()
                user.session_var = 'RENTED'
                db.session.add_all([user, ride, bike])
                db.session.commit()
                print('Rented', form.__dict__)


def return_bike(form, current_user):
    current_ride = RideLog.query.filter_by(user_id = current_user.id, current = 'YES').first()
    if current_ride is not None:
        bike = BikeInfo.query.filter_by(bike_number=current_ride.bike_number).first()
        minutes = current_ride.get_minutes(datetime.utcnow())
        amount = 1 + int(minutes*0.2)
        user = User.query.filter_by(id=current_user.id).first()

        if (form.payment_type == "CARD") or (form.payment_type == "WALLET" and user.wallet_balance > amount):
            current_ride.end_ride(form.location)
            bike.place_back(form.location)

            transaction = Transaction(user_id = current_ride.user_id,
                                       payment_type = form.payment_type,
                                       amount = amount,
                                       ride_id = current_ride.ride_id,
                                       paid = 'NO')
            user.session_var = 'PAYMENT'
            if form.rating:
                review = Review(current_ride.user_id, current_ride.ride_id, form.rating, form.review)
                db.session.add(review)
            db.session.add_all([current_ride, bike, transaction, user])
            db.session.commit()
            print('Returned', form.__dict__)
            return True
        else: return False


def payment(form, current_user):
    transaction = Transaction.query.filter_by(user_id=current_user.id, paid='NO').first()
    if transaction is not None:
        user = User.query.filter_by(id=current_user.id).first()
        if transaction.payment_type.name == 'WALLET':
            user.deduct_wallat_balance(transaction.amount)
            user.session_var = ''
            transaction.update_payment()
            db.session.add_all([user, transaction])
            db.session.commit()
        else:
            ride = RideLog.query.filter_by(ride_id = transaction.ride_id).first()
            today = datetime.today()
            transaction.update_payment(form.card)
            user.session_var = ''
            db.session.add_all([user, transaction])
            db.session.commit()
        print('Payed', form.__dict__)


def add_balance(form, current_user):
    user = User.query.filter_by(id=current_user.id).first()
    user.add_wallet_balance(form.amount)
    topup = TopUp(user_id = user.id,
                   credit_card_number = form.card,
                   amount = form.amount)
    db.session.add_all([user,topup])
    db.session.commit()
    print('Added Balance', form.__dict__)


def report_bike(form, current_user):
    repair = Repair(user_id = current_user.id, bike_number = form.bike_number, description = form.description, urgency=form.urgency)
    bike = BikeInfo.query.filter_by(bike_number=form.bike_number).first()
    if not form.urgency == 'LOW':
        bike.status = 'REPAIR'
    db.session.add_all([repair,bike])
    db.session.commit()
    print('Reported', form.__dict__)





first_name_choices = 'Kent Cian Eamon Emrys Ansel Finnick Chester Evander Lysander Keiran Liesel Aiko Aaralyn Imogen Adora Andromeda Odette Acacia Aoife Alaska Artemis Ocean Adalia Indigo Ash Darcy Avalon Echo Billie Zephyr'.split()
last_name_choices = 'Smith Johnson Williams Brown Jones Garcia Miller Davis Rodriguez Martinez Hernandez Lopez Gonzalez Wilson Anderson Thomas Taylor Moore Jackson Martin Lee Perez Thompson White Harris Sanchez Clark Ramirez Lewis Robinson'.split()
email_suffix_choices = ['', '', '', '', '', '91', '92', '93', '94', '95', '96', '97', '98', '007', 'cool', 'zzz', 'always']
locations = 'HILLHEAD HILLHEAD HILLHEAD HILLHEAD PARTICK PARTICK FINNIESTON FINNIESTON FINNIESTON GOVAN LAURIESTON LAURIESTON'.split()
comments = {1:['', '', '', '', '', '', '', '', 'Bad ride', 'dissapointing ride', 'should take better care of your bikes'], \
            2:['', '', '', '', '', '', '', '', 'Not very good', 'dissapointing', 'bikes not in very good condition'], \
            3:['', '', '', '', '', '', '', '', 'Ok ok', 'Not very good', 'add more locations'], \
            4:['', '', '', '', '', '', '', '', 'Good', 'good service', 'satisfiying ride', 'nice bikes provided'], \
            5:['', '', '', '', '', '', '', '', 'Great ride', 'very good', 'extremely good', 'great service provided by easy ride']}
descriptions = {'LOW':['Small scratch', 'Paint lost', 'Handle is loose'], \
               'MEDIUM':['Handle very loose', 'Frame is rattling', 'Frame bent a bit'], \
               'HIGH':['Handle broken', 'Frame bent', 'Tyre punchured']}
repair_levels = {'LOW':[1,2], 'MEDIUM':[2,3,4], 'HIGH':[3,4,5]}
repair_comments = {1: ['Fixed', 'Small issue'], 2: ['fixed', 'Not a big issue'], 3: ['All done', 'Fixed', 'Able to fix'], 4: ['Big issue', 'issue with handle', 'issue with frame'], 5: ['Type issue', 'issue with handle', 'issue with frame']}


while True:
    time = datetime.today()
    if time.minute == random.choice(range(0,60)):
        # Register user
        try:
            if random.uniform(0, 1000000) < 0.01:
                first_name = random.choice(first_name_choices)
                last_name = random.choice(last_name_choices)
                email_suffix = random.choice(email_suffix_choices)
                form = Cnv2Obj(dict(first_name=first_name, last_name=last_name, phone_number=random.randint(1000000000, 9999999999),
                                    email=first_name+last_name+email_suffix+random.randint(10000, 99999)+'@dummy.test', password='12345666', city='GLASGOW'))
                register_user(form)
        except Exception as e: ''

        # Rent
        try:
            if random.uniform(0, 1000000) < 0.2:
                user = random.choice(User.query.filter_by( user_status='NORMAL').all())
                form = Cnv2Obj(dict(location = random.choice(locations)))
                rent_bike(form, user)
                login_user(form, user)

        except Exception as e: ''

        # Return
        try:
            if random.uniform(0, 1000000) < 0.2:
                user = random.choice(RideLog.query.filter_by( current='YES').all()).user
                rating = random.choice([1,1,1,2,2,3,3,3,3,3,4,4,4,5,5,5,5,5,5,5])
                payment_type = random.choice(['CARD','CARD','WALLET','WALLET','WALLET'])
                form = Cnv2Obj(dict(location = random.choice(locations), payment_type=payment_type,
                                    rating = rating, review = random.choice(comments[rating])))
                if return_bike(form, user):
                    if payment_type == 'WALLET':
                        payment(form, user)
                else:
                    form.payment_type = 'CARD'
                    return_bike(form, user)
        except Exception as e: ''

        # Payment
        try:
            if random.uniform(0, 1000000) < 0.3:
                user = random.choice(Transaction.query.filter_by(paid = 'NO').all()).user
                form = Cnv2Obj(dict(name = 's', card=int(str(random.randint(9999999, 100000000)) + str(random.randint(9999999, 100000000))),
                                month = '05', year = '2023', cvv = '123'))
                payment(form, user)
        except Exception as e: ''

        # TopUp
        try:
            if random.uniform(0, 1000000) < 0.1:
                user = random.choice(User.query.filter_by( user_status='NORMAL').all())
                if user.wallet_balance < 10:
                    form = Cnv2Obj(dict(amount = random.randint(5, 50), name = 's', card=int(str(random.randint(9999999, 100000000)) + str(random.randint(9999999, 100000000))),
                                        month = '05', year = '2023', cvv = '123'))
                    add_balance(form, user)
        except Exception as e: ''

        # Report
        try:
            if random.uniform(0, 1000000) < 0.05:
                user = random.choice(User.query.filter_by( user_status='NORMAL').all())
                bike = random.choice(BikeInfo.query.filter_by(status='YES').all())
                urgency =  random.choice(['LOW','MEDIUM','HIGH'])
                form = Cnv2Obj(dict(bike_number = bike.bike_number, urgency=urgency, description=random.choice(descriptions[urgency])))
                report_bike(form, user)
        except Exception as e: ''

        # Repair bike
        try:
            if random.uniform(0, 1000000) < 0.1:
                user = random.choice(User.query.filter_by(user_type='OPERATOR').all())
                repair = random.choice(Repair.query.filter_by(repair_status='NO').all())
                if BikeInfo.query.filter_by(bike_number=repair.bike_number).first().status.name in ['YES', 'REPAIR']:
                    level_of_repair = random.choice(repair_levels[repair.urgency.name])
                    form = Cnv2Obj(dict(bike_number = repair.bike_number, level_of_repair = level_of_repair,
                                        comment = random.choice(repair_comments[level_of_repair])))
                    repair_bike(form, user)
        except Exception as e: ''
        # Move bike
        try:
            if random.uniform(0, 1000000) < 0.15:
                avl_bikes_raw = dict(BikeInfo.query.with_entities(BikeInfo.last_location.name, db.func.count(BikeInfo.last_location).label('count')).group_by(BikeInfo.last_location).all())
                avl_bikes = dict(format_categories(avl_bikes_raw, ['HILLHEAD', 'PARTICK', 'GOVAN', 'FINNIESTON', 'LAURIESTON']))
                low_number_loc = []
                high_number_loc = max(avl_bikes, key=avl_bikes.get)
                for loc in avl_bikes:
                    if avl_bikes[loc] < 4:
                        low_number_loc.append(loc)
                if low_number_loc:
                    for low_loc in low_number_loc:
                        bike = BikeInfo.query.filter_by(last_location = high_number_loc, status='YES').first()
                        if bike is not None:
                            form = Cnv2Obj(dict(bike_number = bike.bike_number, new_location = low_loc))
                            move_bike(form)
        except Exception as e: ''


    if time.minute == 30:
        # Return all bikes
        try:
            returns = RideLog.query.filter_by( current='YES').all()
            for to_return in returns:
                user = to_return.user
                rating = random.choice([1,1,1,2,2,3,3,3,3,3,4,4,4,5,5,5,5,5,5,5])
                payment_type = random.choice(['CARD','CARD','WALLET','WALLET','WALLET'])
                form = Cnv2Obj(dict(location = random.choice(locations), payment_type=payment_type,
                                      rating = rating, review = random.choice(comments[rating])))
                if return_bike(form, user):
                    if payment_type == 'WALLET':
                        payment(form, user)
                else:
                    form.payment_type = 'CARD'
                    return_bike(form, user)
        except Exception as e: ''
        # Pay all
        try:
            payments = Transaction.query.filter_by(paid = 'NO').all()
            for to_pay in payments:
                user = to_pay.user
                form = Cnv2Obj(dict(name = 's', card=int(str(random.randint(9999999, 100000000)) + str(random.randint(9999999, 100000000))),
                                month = '05', year = '2023', cvv = '123'))
                payment(form, user)
        except Exception as e: ''
