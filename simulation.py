# A simulation bot to act on behalf of both user (for actions registering, renting, paying etc) and an operator (for moving and repairing)
# This is used to run in AWS EC2 instance where it runs continuosly in the background  in order to test the solution

from datetime import datetime
import random
from flask import Flask
from easy_ride.models import User, LoginLog, RideLog, Transaction, Review, Repair, BikeInfo, TopUp
from easy_ride import db
from easy_ride.helpers import format_categories, Cnv2Obj


# Repair function for operator
def repair_bike(form, current_user):
    repair = Repair.query.filter_by(bike_number=form.bike_number, repair_status='NO').first() # Get the repair for the bike
    repair.repaired(current_user.id, form.level_of_repair, form.comment) #Update the record with details from operator
    bike = BikeInfo.query.filter_by(bike_number=repair.bike_number).first() #Get bike info and update the status from REPAIR to YES (Available)
    bike.status = 'YES'
    db.session.add_all([repair, bike]) #Add and commit the changes to the database
    db.session.commit()
    print(datetime.today(),',', 'OPERATOR: repaired',',', form.__dict__, )

# Move function for operator
def move_bike(form):
    bike = BikeInfo.query.filter_by(bike_number=form.bike_number).first() #Get the bike from database
    bike.place_back(form.new_location) # Update the bike location
    db.session.add(bike) #Add and commit the changes to the database
    db.session.commit()
    print(datetime.today(),',', 'OPERATOR: moved',',', form.__dict__)

# Register function for user
def register_user(form):
    user = User(first_name=form.first_name, last_name=form.last_name, phone_number=form.phone_number, email=form.email,
                password=form.password, city=form.city, user_type='NORMAL') # Add new user details
    db.session.add(user) #Add and commit the changes to the database
    db.session.commit()
    print(datetime.today(),',', 'Registered',',', form.__dict__)

# Login function for user
def login_user(form, current_user):
    login_log = LoginLog(current_user.id, current_user.user_type.name) # Add new loging log
    db.session.add(login_log) #Add and commit the changes to the database
    db.session.commit()
    print(datetime.today(),',', 'Logged In',',', {'user_id': current_user.id, 'user_type': current_user.user_type.name})

# Rent function for user
def rent_bike(form, current_user):
    current_rides = RideLog.query.filter_by(user_id = current_user.id, current = 'YES').first() # Get the on-going rides of the user
    payment = Transaction.query.filter_by(user_id = current_user.id, paid = 'NO').first() # Get the pending payments of the user
    if payment is None and current_rides is None: # If there are no pending payments or on-going rides only then allow them to rent
        bike = BikeInfo.query.filter_by(last_location=form.location, status='YES').first() # Get a random available bike from the selected location
        if bike is not None:
            ride = RideLog(user_id = current_user.id, bike_number = bike.bike_number, start_location = form.location, current = "YES") # Create a ride for the user
            bike.status = 'NO' # Update the bike status from YES (available) to 'NO' (not available)
            user = User.query.filter_by(id=current_user.id).first() # Get the user details and update the session variable to control the options available to him on the dashboard
            user.session_var = 'RENTED'
            db.session.add_all([user, ride, bike]) #Add and commit the changes to the database
            db.session.commit()
            print(datetime.today(),',', 'Rented',',', form.__dict__)

# Return function for user
def return_bike(form, current_user):
    current_ride = RideLog.query.filter_by(user_id = current_user.id, current = 'YES').first() # Get the on-going ride of the user
    if current_ride is not None: # IF there is an on-going ride only hten allow him to return
        bike = BikeInfo.query.filter_by(bike_number=current_ride.bike_number).first() # Get the bike info of the ride
        minutes = current_ride.get_minutes(datetime.utcnow())
        amount = 1 + int(minutes*0.2) # Calculate the amount to charge the user
        user = User.query.filter_by(id=current_user.id).first() # Get the user details

        # Only allow to proceed to payment if a user choose to pay with card or has enough balance in the wallet to pay
        if (form.payment_type == "CARD") or (form.payment_type == "WALLET" and user.wallet_balance > amount):
            # Update the ride_log, add a transaction and update the bike status
            current_ride.end_ride(form.location)
            bike.place_back(form.location)
            transaction = Transaction(user_id = current_ride.user_id,
                                       payment_type = form.payment_type,
                                       amount = amount,
                                       ride_id = current_ride.ride_id,
                                       paid = 'NO')
            user.session_var = 'PAYMENT'
            # Add rating if given
            if form.rating:
                review = Review(current_ride.user_id, current_ride.ride_id, form.rating, form.review)
                db.session.add(review)
            db.session.add_all([current_ride, bike, transaction, user]) #Add and commit the changes to the database
            db.session.commit()
            print(datetime.today(),',', 'Returned',',', form.__dict__)
            return True
        else: return False

# Payment function for user
def payment(form, current_user):
    transaction = Transaction.query.filter_by(user_id=current_user.id, paid='NO').first() # Check any pending payments to be made for the user
    if transaction is not None:
        user = User.query.filter_by(id=current_user.id).first()
        # Deduct from wallet or card as specified by the user at end of the ride
        if transaction.payment_type.name == 'WALLET':
            user.deduct_wallat_balance(transaction.amount)
            user.session_var = ''
            transaction.update_payment()
        else:
            ride = RideLog.query.filter_by(ride_id = transaction.ride_id).first()
            today = datetime.today()
            transaction.update_payment(form.card)
            user.session_var = ''
        db.session.add_all([user, transaction]) #Add and commit the changes to the database
        db.session.commit()
        print(datetime.today(),',', 'Payed',',', form.__dict__)

# Balance function for user
def add_balance(form, current_user):
    # Get user details and add to the current balance
    user = User.query.filter_by(id=current_user.id).first()
    user.add_wallet_balance(form.amount)
    # Add a topup transaction
    topup = TopUp(user_id = user.id,
                   credit_card_number = form.card,
                   amount = form.amount)
    db.session.add_all([user,topup]) #Add and commit the changes to the database
    db.session.commit()
    print(datetime.today(),',', 'Added Balance',',', form.__dict__)

# Report function for user
def report_bike(form, current_user):
    repair = Repair(user_id = current_user.id, bike_number = form.bike_number, description = form.description, urgency=form.urgency) # Create a repair record
    bike = BikeInfo.query.filter_by(bike_number=form.bike_number).first()
    # Only make the bike unavailble to others if the urgency is medium or high not low
    if not form.urgency == 'LOW':
        bike.status = 'REPAIR'
    db.session.add_all([repair,bike]) #Add and commit the changes to the database
    db.session.commit()
    print(datetime.today(),',', 'Reported',',', form.__dict__)


chance = 500000 # Probabilty factor to control how often the simulation performs any given actions

# Variables with random values required for some actions
# Required for registering the new users
first_name_choices = 'Kent Cian Eamon Emrys Ansel Finnick Chester Evander Lysander Keiran Liesel Aiko Aaralyn Imogen Adora Andromeda Odette Acacia Aoife Alaska Artemis Ocean Adalia Indigo Ash Darcy Avalon Echo Billie Zephyr'.split()
last_name_choices = 'Smith Johnson Williams Brown Jones Garcia Miller Davis Rodriguez Martinez Hernandez Lopez Gonzalez Wilson Anderson Thomas Taylor Moore Jackson Martin Lee Perez Thompson White Harris Sanchez Clark Ramirez Lewis Robinson'.split()
email_suffix_choices = ['', '', '', '', '', '91', '92', '93', '94', '95', '96', '97', '98', '007', 'cool', 'zzz', 'always']
# Required for renting, returning and rating the rides for the users
locations = 'HILLHEAD HILLHEAD HILLHEAD HILLHEAD PARTICK PARTICK FINNIESTON FINNIESTON FINNIESTON GOVAN LAURIESTON LAURIESTON'.split() # Same location given multiple times to control the probabilty for each location
comments = {1:['', '', '', '', '', '', '', '', 'Bad ride', 'dissapointing ride', 'should take better care of your bikes'], \
            2:['', '', '', '', '', '', '', '', 'Not very good', 'dissapointing', 'bikes not in very good condition'], \
            3:['', '', '', '', '', '', '', '', 'Ok ok', 'Not very good', 'add more locations'], \
            4:['', '', '', '', '', '', '', '', 'Good', 'good service', 'satisfiying ride', 'nice bikes provided'], \
            5:['', '', '', '', '', '', '', '', 'Great ride', 'very good', 'extremely good', 'great service provided by easy ride']} # Different comment for different ratings
#  required for reporting a bike by the users
descriptions = {'LOW':['Small scratch', 'Paint lost', 'Handle is loose'], \
               'MEDIUM':['Handle very loose', 'Frame is rattling', 'Frame bent a bit'], \
               'HIGH':['Handle broken', 'Frame bent', 'Tyre punchured']} # Different desciptions for different level of repairs for users to report
# Required for repairing for the operators
repair_levels = {'LOW':[1,2], 'MEDIUM':[2,3,4], 'HIGH':[3,4,5]}
repair_comments = {1: ['Fixed', 'Small issue'], 2: ['fixed', 'Not a big issue'], 3: ['All done', 'Fixed', 'Able to fix'], 4: ['Big issue', 'issue with handle', 'issue with frame'], 5: ['Type issue', 'issue with handle', 'issue with frame']}

# Keep the script running
while True:
    time = datetime.today()
    if time.minute in random.choices(range(0,60), k=3):  # A way to control the probability
        # Register user
        try:
            if random.uniform(0, chance) < 0.005: # A way to control the probability
            # Get random details of name, email and register a new user
                first_name = random.choice(first_name_choices)
                last_name = random.choice(last_name_choices)
                email_suffix = random.choice(email_suffix_choices)
                form = Cnv2Obj(dict(first_name=first_name, last_name=last_name, phone_number=random.randint(1000000000, 9999999999),
                                    email=first_name+last_name+email_suffix+str(random.randint(10000, 99999))+'@dummy.test', password='12345666', city='GLASGOW'))
                register_user(form)
        except Exception as e: ''

        # Rent
        try:
            if random.uniform(0, chance) < 10: # A way to control the probability
            # Choose a random user then both perform a login and also rent a bike from him from a random location
                user = random.choice(User.query.filter_by( user_type='NORMAL').all())
                if user.first_name in first_name_choices:
                    form = Cnv2Obj(dict(location = random.choice(locations)))
                    login_user(form, user)
                    rent_bike(form, user)
        except Exception as e: ''

        # Return
        try:
            if random.uniform(0, chance) < 1: # A way to control the probability
            # Choose a random on going ride then finish ride with random payment method, a random rating and comment
                user = random.choice(RideLog.query.filter_by( current='YES').all()).user
                if user.first_name in first_name_choices:
                    rating = random.choice([1,1,1,2,2,3,3,3,3,3,4,4,4,5,5,5,5,5,5,5])
                    payment_type = random.choice(['CARD','CARD','WALLET','WALLET','WALLET'])
                    form = Cnv2Obj(dict(location = random.choice(locations), payment_type=payment_type,
                                        rating = rating, review = random.choice(comments[rating])))

                    if return_bike(form, user): # If return is succesful i.e. choosen card or have enough balance to pay via the wallet
                        if payment_type == 'WALLET': # If choosen to pay with wallet then deduct balance from the users wallet and update the transaction
                            payment(form, user)
                    else:
                        form.payment_type = 'CARD' # If choose to pay with wallet but doesnt have enough balance to pay then update the payment method to card and return the bike
                        return_bike(form, user)
        except Exception as e: ''

        # Payment
        try:
            if random.uniform(0, chance) < 2: # A way to control the probability
            # Choose a random pending payment and finish the payment with random card details
                user = random.choice(Transaction.query.filter_by(paid = 'NO').all()).user
                if user.first_name in first_name_choices:
                    form = Cnv2Obj(dict(name = 's', card=int(str(random.randint(9999999, 100000000)) + str(random.randint(9999999, 100000000))),
                                    month = '05', year = '2023', cvv = '123'))
                    payment(form, user)
        except Exception as e: ''

        # TopUp
        try:
            if random.uniform(0, chance) < 1: # A way to control the probability
            # Choose a random user and topup the wallet balance if it is below 10
                user = random.choice(User.query.filter_by( user_type='NORMAL').all())
                if user.first_name in first_name_choices:
                    if user.wallet_balance < 10:
                        form = Cnv2Obj(dict(amount = random.randint(5, 50), name = 's', card=int(str(random.randint(9999999, 100000000)) + str(random.randint(9999999, 100000000))),
                                            month = '05', year = '2023', cvv = '123'))
                        add_balance(form, user)
        except Exception as e: ''

        # Report
        try:
            if random.uniform(0, chance) < 1: # A way to control the probability
            # Choose a random user and have him report a random bike with random urgency and descriptions
                user = random.choice(User.query.filter_by( user_type='NORMAL').all())
                if user.first_name in first_name_choices:
                    bike = random.choice(BikeInfo.query.filter_by(status='YES').all())
                    urgency =  random.choice(['LOW','MEDIUM','HIGH'])
                    form = Cnv2Obj(dict(bike_number = bike.bike_number, urgency=urgency, description=random.choice(descriptions[urgency])))
                    report_bike(form, user)
        except Exception as e: ''

        # Repair bike
        try:
            if random.uniform(0, chance) < 1: # A way to control the probability
            # Choose a random report and have a random operator repair it with random level of repair and random comments
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
            if random.uniform(0, chance) < 10: # A way to control the probability
            # Check if there are less than 4 bikes in any location, then move bike to each of those location from a location with most bikes
                avl_bikes_raw = dict(BikeInfo.query.filter_by(status = 'YES').with_entities(BikeInfo.last_location.name, db.func.count(BikeInfo.last_location).label('count')).group_by(BikeInfo.last_location).all())
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

    # Every one hour finsh all the on-going rides and all pending repairs
    if time.minute == 30:
        # Return all bikes
        try:
            returns = RideLog.query.filter_by( current='YES').all() # Get all on going rides
            for to_return in returns:
                # Choose a random on going ride then finish ride with random payment method, a random rating and comment
                user = to_return.user
                if user.first_name in first_name_choices:
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
            payments = Transaction.query.filter_by(paid = 'NO').all() # Get all pending payments
            for to_pay in payments:
                # Choose a random pending payment and finish the payment with random card details
                user = to_pay.user
                if user.first_name in first_name_choices:
                    form = Cnv2Obj(dict(name = 's', card=int(str(random.randint(9999999, 100000000)) + str(random.randint(9999999, 100000000))),
                                    month = '05', year = '2023', cvv = '123'))
                    payment(form, user)
        except Exception as e: ''
