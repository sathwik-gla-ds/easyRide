# contains the routes related to employees pages such as operator and manager dashboards, bikes info, rides info etc

from flask import render_template,url_for,flash,redirect,request,Blueprint
from flask_login import current_user, login_required
from easy_ride import db
from easy_ride.helpers import check_user_type, format_days, monthdelta, format_months, format_categories
from easy_ride.models import RideLog, BikeInfo, Repair, Transaction, User, LoginLog, Review
from easy_ride.employees.forms import MoveBikeForm, RepairBikeForm, AddOperatorForm
from datetime import date, timedelta


employees = Blueprint('employees',__name__) # For registering the Blueprint/folder in main __init__.py file


# Operator Dashboard page
@employees.route("/operator_view")
@login_required
@check_user_type('OPERATOR') # Access only to operator and requires to be logged in
def operator_view():
    locations = BikeInfo.query.filter_by(status='YES').with_entities(BikeInfo.last_location, db.func.count(BikeInfo.last_location) \
                                .label('count')).group_by(BikeInfo.last_location).all() # Get the available bike count grouped by locations
    rides = RideLog.query.filter_by(current = 'YES').count() # Get the current on going ride count
    payments = Transaction.query.filter_by(paid = 'NO').count() # Get teh pending payments count
    repairs = Repair.query.filter_by(repair_status = 'NO').count() # Get the pending reports count
    return render_template('operator_home.html', locations = locations, rides = rides, payments = payments, repairs = repairs) # Page to use/render when user visits the route


# page for checking the ride logs
@employees.route("/check_rides")
@login_required
@check_user_type(['OPERATOR', 'MANAGER'])  # Access only to operator and manager and requires to be logged in
def check_rides():
    status = request.args.get('status', 'YES') # Table filter for ride status
    page = request.args.get('page', 1, type=int) # filter for page number (pagenation)
    if status == 'YES':
        rides = RideLog.query.filter_by(current = 'YES').order_by(RideLog.start_time.asc()).paginate(page=page, per_page=30) #Get the on-going ride records
    elif status == 'PENDING':
        rides = Transaction.query.filter_by(paid = 'NO').order_by(Transaction.id.asc()).paginate(page=page, per_page=30) #Get the pending payment records
    else:
        rides = RideLog.query.filter_by(current = 'NO').order_by(RideLog.start_time.desc()).paginate(page=page, per_page=30) #Get the past ride records
    return render_template('check_rides.html', rides=rides, status=status)  # Page to use/render when user visits the route


# Page for checking all the bikes and track them
@employees.route("/check_bikes")
@login_required
@check_user_type(['OPERATOR', 'MANAGER'])  # Access only to operator and manager and requires to be logged in
def check_bikes():
    page = request.args.get('page', 1, type=int) # filter for page number (pagenation)
    filter_by_status = request.args.get('f_s', '') #All, Free, On-going, Repair, Disabled (Bike status filter)
    filter_by_location = request.args.get('f_l', '') #All, HILLHEAD, PARTICK, FINNIESTON, GOVAN, LAURIESTON (location filter)
    filter_by_number = request.args.get('bike_num', '') #Bike number filter

    # Get the bike records based on the filters requested
    if filter_by_status and filter_by_location:
        bikes = BikeInfo.query.filter_by(status = filter_by_status, last_location = filter_by_location).paginate(page=page, per_page=20)
    elif not filter_by_status and filter_by_location:
        bikes = BikeInfo.query.filter_by(last_location = filter_by_location).paginate(page=page, per_page=20)
    elif filter_by_status and not filter_by_location:
        bikes = BikeInfo.query.filter_by(status = filter_by_status).paginate(page=page, per_page=20)
    elif filter_by_number:
        bikes = BikeInfo.query.filter_by(bike_number = filter_by_number).paginate(page=page, per_page=20)
    else:
        bikes = BikeInfo.query.paginate(page=page, per_page=20)

    return render_template('check_bikes.html', bikes=bikes, p=page, f_s = filter_by_status, f_l = filter_by_location, bike_num = filter_by_number) # Page to use/render when user visits the route


# Page for repairing the bikes
@employees.route("/repair_bike",methods=['GET','POST'])
@login_required
@check_user_type('OPERATOR')  # Access only to operator and requires to be logged in
def repair_bike():
    form = RepairBikeForm() # Form for filling in the repair details
    page = request.args.get('page', 1, type=int)
    repairs = Repair.query.filter_by(repair_status = 'NO').paginate(page=page, per_page=20) # Get the pending repairs

    # Logic to perform after filling in the form
    if form.validate_on_submit():
        repair = Repair.query.filter_by(bike_number=form.bike_number.data, repair_status='NO').first() # Get repair details
        repair.repaired(current_user.id, form.level_of_repair.data, form.comment.data)
        bike = BikeInfo.query.filter_by(bike_number=repair.bike_number).first() # Update the bike status
        bike.status = 'YES'
        db.session.add_all([repair, bike]) #Add and commit the changes to the database
        db.session.commit()
        flash('Repair success!') # Flash a success message
        return redirect(url_for('employees.check_bikes', bike_num=bike.bike_number)) # Redirect to the bikes pages after filling in the form

    return render_template('repair_bike.html', form=form, repairs=repairs) # Page to use/render when user visits the route


# PAge for moving bikes
@employees.route("/move_bike",methods=['GET','POST'])
@login_required
@check_user_type('OPERATOR')  # Access only to operator and requires to be logged in
def move_bike():
    form = MoveBikeForm() # Form for filling in to move the bike

    # Logic to perform after filling in the form
    if form.validate_on_submit():
        bike = BikeInfo.query.filter_by(bike_number=form.bike_number.data).first() # Update the bike location
        bike.place_back(form.new_location.data)
        db.session.add(bike) #Add and commit the changes to the database
        db.session.commit()
        flash('Move success!') # Flash a success message
        return redirect(url_for('employees.check_bikes', bike_num=bike.bike_number)) # Redirect to the bikes pages after filling in the form

    return render_template('move_bike.html', form=form) # Page to use/render when user visits the route


# PAge for viewing the current operators and adding new ones
@employees.route("/operators",methods=['GET','POST'])
@login_required
@check_user_type('MANAGER')  # Access only to manager and requires to be logged in
def operators():
    form = AddOperatorForm() # Form for filling in to add new operators
    page = request.args.get('page', 1, type=int)
    operators = User.query.filter_by(user_type = 'OPERATOR').paginate(page=page, per_page=20)

    # Logic to perform after filling in the form
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    phone_number=form.phone_number.data,
                    email=form.email.data,
                    password=form.password.data,
                    city=form.city.data,
                    user_type='OPERATOR') # Create new operator user

        db.session.add(user) #Add and commit the changes to the database
        db.session.commit()
        flash('Operator successfully registered!') # Flash a success message
        return redirect(url_for('employees.operators')) # Reload the same page with updated talbe after filling in the form

    return render_template('operators.html', form=form, operators=operators) # Page to use/render when user visits the route


# Page for checking details of all the users
@employees.route("/users",methods=['GET','POST'])
@login_required
@check_user_type('MANAGER')  # Access only to manager and requires to be logged in
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.filter_by(user_type = 'NORMAL').paginate(page=page, per_page=30)

    return render_template('users.html', users=users) # Page to use/render when user visits the route


# Manager dashboard page
@employees.route("/manager_view")
@login_required
@check_user_type('MANAGER')  # Access only to manager and requires to be logged in
def manager_view():
    filter_by_time = request.args.get('time', 'day') #day, month, year (time filter for the graphs)

    # New users - bar (Get user count data required for the graph grouped by the time filter)
    if filter_by_time == 'day':
        new_reg_raw = dict(User.query.filter_by(user_type='NORMAL').filter(User.created_at > (date.today() - timedelta(7)))\
                                .with_entities(db.func.date(User.created_at), db.func.count(User.id).label('count'))\
                                                        .group_by(db.func.date(User.created_at)).all())
        new_reg = format_days(new_reg_raw)
    elif filter_by_time == 'month':
        new_reg_raw = dict(User.query.filter_by(user_type='NORMAL').filter(User.created_at > monthdelta(date.today(), -6))\
                                .with_entities(db.func.month(User.created_at), db.func.count(User.id).label('count'))\
                                                        .group_by(db.func.month(User.created_at)).all())
        new_reg = format_months(new_reg_raw)
    else:
        new_reg = User.query.filter_by(user_type='NORMAL').with_entities(db.func.year(User.created_at), db.func.count(User.id).label('count'))\
                                .group_by(db.func.year(User.created_at)).all()

    #   Active users - line (Get unique logins count data required for the graph grouped by the time filter)
    if filter_by_time == 'day':
        login_log_raw = dict(LoginLog.query.filter_by(user_type='NORMAL').filter(LoginLog.logged_at > (date.today() - timedelta(7)))\
                                .with_entities(db.func.date(LoginLog.logged_at), db.func.count(db.func.distinct(LoginLog.user_id)).label('count'))\
                                                        .group_by(db.func.date(LoginLog.logged_at)).all())
        login_log = format_days(login_log_raw)
    elif filter_by_time == 'month':
        login_log_raw = dict(LoginLog.query.filter_by(user_type='NORMAL').filter(LoginLog.logged_at > monthdelta(date.today(), -6))\
                                .with_entities(db.func.month(LoginLog.logged_at), db.func.count(db.func.distinct(LoginLog.user_id)).label('count'))\
                                                        .group_by(db.func.month(LoginLog.logged_at)).all())
        login_log = format_months(login_log_raw)
    else:
        login_log = LoginLog.query.filter_by(user_type='NORMAL')\
                                .with_entities(db.func.year(LoginLog.logged_at), db.func.count(db.func.distinct(LoginLog.user_id)).label('count'))\
                                .group_by(db.func.year(LoginLog.logged_at)).all()

    # Total rides - line (Get rides count data required for the graph grouped by the time filter)
    if filter_by_time == 'day':
        ride_log_raw = dict(RideLog.query.filter_by(current='NO').filter(RideLog.end_time > (date.today() - timedelta(7)))\
                                .with_entities(db.func.date(RideLog.end_time), db.func.count(RideLog.id).label('count'))\
                                                        .group_by(db.func.date(RideLog.end_time)).all())
        ride_log = format_days(ride_log_raw)
    elif filter_by_time == 'month':
        ride_log_raw = dict(RideLog.query.filter_by(current='NO').filter(RideLog.end_time > monthdelta(date.today(), -6))\
                                .with_entities(db.func.month(RideLog.end_time), db.func.count(RideLog.id).label('count'))\
                                                        .group_by(db.func.month(RideLog.end_time)).all())
        ride_log = format_months(ride_log_raw)
    else:
        ride_log = RideLog.query.filter_by(current='NO').with_entities(db.func.year(RideLog.end_time), db.func.count(RideLog.id).label('count'))\
                                .group_by(db.func.year(RideLog.end_time)).all()

    # Available bikes - doughnut (Get available bike location count data required for the graph grouped by locations)
    avl_bikes_raw = dict(BikeInfo.query.filter_by(status='YES')\
                            .with_entities(BikeInfo.last_location.name, db.func.count(BikeInfo.last_location).label('count'))\
                                                    .group_by(BikeInfo.last_location).all())
    avl_bikes = format_categories(avl_bikes_raw, ['HILLHEAD', 'PARTICK', 'GOVAN', 'FINNIESTON', 'LAURIESTON'])

    #  Popular location - doughnut  (Get popular ride start location count data required for the graph grouped by locations and filtered by time )
    if filter_by_time == 'day':
        pop_loc_raw = dict(RideLog.query.filter_by(current='NO').filter(RideLog.end_time > (date.today() - timedelta(7)))\
                                .with_entities(RideLog.start_location.name, db.func.count(RideLog.id).label('count'))\
                                                        .group_by(RideLog.start_location).all())
        pop_loc = format_categories(pop_loc_raw, ['HILLHEAD', 'PARTICK', 'GOVAN', 'FINNIESTON', 'LAURIESTON'])
    elif filter_by_time == 'month':
        pop_loc_raw = dict(RideLog.query.filter_by(current='NO').filter(RideLog.end_time > monthdelta(date.today(), -6))\
                                .with_entities(RideLog.start_location.name, db.func.count(RideLog.id).label('count'))\
                                                        .group_by(RideLog.start_location).all())
        pop_loc = format_categories(pop_loc_raw, ['HILLHEAD', 'PARTICK', 'GOVAN', 'FINNIESTON', 'LAURIESTON'])
    else:
        pop_loc_raw = dict(RideLog.query.filter_by(current='NO').with_entities(RideLog.start_location.name, db.func.count(RideLog.id).label('count'))\
                                .group_by(RideLog.start_location).all())
        pop_loc = format_categories(pop_loc_raw, ['HILLHEAD', 'PARTICK', 'GOVAN', 'FINNIESTON', 'LAURIESTON'])

    # Wallet vs Card times - radar  (Get wallet vs card used count data required for the graph grouped by time and payment type)
    if filter_by_time == 'day':
        pay_type_raw = Transaction.query.filter_by(paid='YES').filter(Transaction.time > (date.today() - timedelta(7)))\
                                .with_entities(db.func.date(Transaction.time), Transaction.payment_type.name, db.func.count(Transaction.id).label('count'))\
                                                        .group_by(db.func.date(Transaction.time), Transaction.payment_type).all()
        pay_type_raw_wallet = []
        pay_type_raw_card = []
        for pay in pay_type_raw:
            if pay[1] == 'CARD':
                pay_type_raw_card.append((pay[0], pay[2]))
            else:
                pay_type_raw_wallet.append((pay[0], pay[2]))
        pay_type_wallet = format_days(dict(pay_type_raw_wallet))
        pay_type_card = format_days(dict(pay_type_raw_card))
    elif filter_by_time == 'month':
        pay_type_raw = Transaction.query.filter_by(paid='YES').filter(Transaction.time > monthdelta(date.today(), -6))\
                                .with_entities(db.func.month(Transaction.time), Transaction.payment_type.name, db.func.count(Transaction.id).label('count'))\
                                                        .group_by(db.func.month(Transaction.time), Transaction.payment_type).all()
        pay_type_raw_wallet = []
        pay_type_raw_card = []
        for pay in pay_type_raw:
            if pay[1] == 'CARD':
                pay_type_raw_card.append((pay[0], pay[2]))
            else:
                pay_type_raw_wallet.append((pay[0], pay[2]))
        pay_type_wallet = format_months(dict(pay_type_raw_wallet))
        pay_type_card = format_months(dict(pay_type_raw_card))
    else:
        pay_type_raw = Transaction.query.filter_by(paid='YES')\
                                .with_entities(db.func.year(Transaction.time), Transaction.payment_type.name, db.func.count(Transaction.id).label('count'))\
                                                        .group_by(db.func.year(Transaction.time), Transaction.payment_type).all()
        pay_type_wallet = []
        pay_type_card = []
        for pay in pay_type_raw:
            if pay[1] == 'CARD':
                pay_type_raw_card.append((pay[0], pay[2]))
            else:
                pay_type_raw_wallet.append((pay[0], pay[2]))

    # Wallet vs Card amount - radar (Get wallet vs card payed amount data required for the graph grouped by time and payment type)
    if filter_by_time == 'day':
        pay_amount_raw = Transaction.query.filter_by(paid='YES').filter(Transaction.time > (date.today() - timedelta(7)))\
                                .with_entities(db.func.date(Transaction.time), Transaction.payment_type.name, db.func.sum(Transaction.amount).label('count'))\
                                                        .group_by(db.func.date(Transaction.time), Transaction.payment_type).all()
        pay_amount_raw_wallet = []
        pay_amount_raw_card = []
        for pay in pay_amount_raw:
            if pay[1] == 'CARD':
                pay_amount_raw_card.append((pay[0], pay[2]))
            else:
                pay_amount_raw_wallet.append((pay[0], pay[2]))
        pay_amount_wallet = format_days(dict(pay_amount_raw_wallet))
        pay_amount_card = format_days(dict(pay_amount_raw_card))
    elif filter_by_time == 'month':
        pay_amount_raw = Transaction.query.filter_by(paid='YES').filter(Transaction.time > monthdelta(date.today(), -6))\
                                .with_entities(db.func.month(Transaction.time), Transaction.payment_type.name, db.func.sum(Transaction.amount).label('count'))\
                                                        .group_by(db.func.month(Transaction.time), Transaction.payment_type).all()
        pay_amount_raw_wallet = []
        pay_amount_raw_card = []
        for pay in pay_amount_raw:
            if pay[1] == 'CARD':
                pay_amount_raw_card.append((pay[0], pay[2]))
            else:
                pay_amount_raw_wallet.append((pay[0], pay[2]))
        pay_amount_wallet = format_months(dict(pay_amount_raw_wallet))
        pay_amount_card = format_months(dict(pay_amount_raw_card))
    else:
        pay_amount_raw = Transaction.query.filter_by(paid='YES')\
                                .with_entities(db.func.year(Transaction.time), Transaction.payment_type.name, db.func.sum(Transaction.amount).label('count'))\
                                                        .group_by(db.func.year(Transaction.time), Transaction.payment_type).all()
        pay_amount_wallet = []
        pay_amount_card = []
        for pay in pay_amount_raw:
            if pay[1] == 'CARD':
                pay_amount_raw_card.append((pay[0], pay[2]))
            else:
                pay_amount_raw_wallet.append((pay[0], pay[2]))

    # Sales - line (Add up wallet and card payed amount data aquired above to get total sales required for the graph)
    total_sales = dict()
    for pay in dict(pay_amount_wallet):
        total_sales[pay] = dict(pay_amount_wallet)[pay] + dict(pay_amount_card)[pay]
    total_sales = list(total_sales.items())

    # Rating - bar (Get ratings data required for the graph grouped by rating and filtered by time)
    if filter_by_time == 'day':
        ratings_raw = dict(Review.query.filter(Review.reviewed_at > (date.today() - timedelta(7)))\
                                .with_entities(Review.rating, db.func.count(Review.id).label('count')).group_by(Review.rating).all())
        ratings = format_categories(ratings_raw, [1,2,3,4,5])
    elif filter_by_time == 'month':
        ratings_raw = dict(Review.query.filter(Review.reviewed_at > monthdelta(date.today(), -6))\
                                .with_entities(Review.rating, db.func.count(Review.id).label('count')).group_by(Review.rating).all())
        ratings = format_categories(ratings_raw, [1,2,3,4,5])
    else:
        ratings_raw = dict(Review.query.with_entities(Review.rating, db.func.count(Review.id).label('count')).group_by(Review.rating).all())
        ratings = format_categories(ratings_raw, [1,2,3,4,5])

    # Latest comments (Get recent 50 comment)
    comments = Review.query.filter(Review.review != "").order_by(Review.reviewed_at.desc()).limit(50).all()

    # Pending repairs -bar (Get pending repairs required for the graph grouped by urgency)
    pending_repairs_raw = dict(Repair.query.filter_by(repair_status='NO').with_entities(Repair.urgency.name, db.func.count(Repair.id).label('count'))\
                            .group_by(Repair.urgency).all())
    pending_repairs = format_categories(pending_repairs_raw, ['LOW', 'MEDIUM', 'HIGH'])

    # Completed repairs - bar (Get completed repairs required for the graph grouped by time filter)
    if filter_by_time == 'day':
        completed_repairs_raw = dict(Repair.query.filter_by(repair_status='YES').filter(Repair.repaired_at > (date.today() - timedelta(7)))\
                                .with_entities(Repair.level_of_repair, db.func.count(Repair.id).label('count')).group_by(Repair.level_of_repair).all())
        completed_repairs = format_categories(completed_repairs_raw, [1,2,3,4,5])
    elif filter_by_time == 'month':
        completed_repairs_raw = dict(Repair.query.filter_by(repair_status='YES').filter(Repair.repaired_at > monthdelta(date.today(), -6))\
                                .with_entities(Repair.level_of_repair, db.func.count(Repair.id).label('count')).group_by(Repair.level_of_repair).all())
        completed_repairs = format_categories(completed_repairs_raw, [1,2,3,4,5])
    else:
        completed_repairs_raw = dict(Repair.query.filter_by(repair_status='YES')\
                                .with_entities(Repair.level_of_repair, db.func.count(Repair.id).label('count')).group_by(Repair.level_of_repair).all())
        completed_repairs = format_categories(completed_repairs_raw, [1,2,3,4,5])

    # Page to use/render when user visits the route along with all the data required to load the graphs
    return render_template('manager_home.html',
                            new_reg = {'data':new_reg},
                            login_log = {'data':login_log},
                            ride_log = {'data':ride_log},
                            avl_bikes = {'data':avl_bikes},
                            pop_loc = {'data':pop_loc},
                            pay_type_wallet = {'data':pay_type_wallet},
                            pay_type_card = {'data':pay_type_card},
                            pay_amount_wallet = {'data':pay_amount_wallet},
                            pay_amount_card = {'data':pay_amount_card},
                            total_sales = {'data':total_sales},
                            ratings = {'data':ratings},
                            comments = comments,
                            pending_repairs = {'data':pending_repairs},
                            completed_repairs = {'data':completed_repairs},
                            time=filter_by_time)
