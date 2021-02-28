# contains the routes related to user account pages such as profile update, adding balance, reporting defective bike

from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from easy_ride import db
from easy_ride.models import User, LoginLog, Transaction, Review, Repair, BikeInfo, TopUp
from easy_ride.users.forms import RegistrationForm, LoginForm, UpdateUserForm, AddBalanceForm, ReportBikeForm
from easy_ride.users.picture_handler import add_profile_pic
from easy_ride.helpers import check_user_type

users = Blueprint('users', __name__)  # For registering the Blueprint/folder in main __init__.py file


# Logout route
@users.route("/logout")
@login_required
def logout():
    logout_user()  # Logout the user from the session and load the home page
    return redirect(url_for("core.index"))


# Registration page
@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Form for filling in for user details

    if form.validate_on_submit():  # Logic to perform after filling in the form
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    phone_number=form.phone_number.data,
                    email=form.email.data,
                    password=form.password.data,
                    city=form.city.data,
                    user_type='NORMAL')  # Create new user record

        db.session.add(user)  # Add and commit the changes to the database
        db.session.commit()
        flash('Thank you for registering in our application!', 'success')
        return redirect(url_for('users.login'))  # redirect to login page after submitting the form

    return render_template('register.html', form=form)  # Laod the registration page


# login page
@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # If user is already authenticated when visiting this page, log them out first
        logout_user()
    form = LoginForm()  # Form for filling in for loging in
    if form.validate_on_submit():  # Logic to perform after filling in the form
        user = User.query.filter_by(email=form.email.data.lower(), user_status='NORMAL').first()  # Check if user exists
        if user is not None:
            if user.check_password(form.password.data):  # Check if the entered password is correct
                login_user(user)  # Use the login_user function to store the user details throughout the session
                flash('Logged in Successfully!', 'success')
                login_log = LoginLog(user.id,
                                     user.user_type.name)  # Add the login record to the login logs and update the database
                db.session.add(login_log)
                db.session.commit()
                next = request.args.get('next')  # Check if there is a page to load after logging in
                if next == None or not next[0] == '/':  # redirect to the appropiate page based on the user type
                    if user.user_type.name == 'NORMAL':
                        next = url_for('core.index')
                    elif user.user_type.name == 'OPERATOR':
                        next = url_for('employees.operator_view')
                    else:
                        next = url_for('employees.manager_view')
                return redirect(next)  # If there is a next page to load redirect to that page
            else:
                flash('Please enter the correct password!', 'danger')
        else:
            flash('This email id is not registered with us!', 'info')
    return render_template('login.html', form=form)


# profile page (can also update user details)
@users.route('/account', methods=['GET', 'POST'])
@login_required
@check_user_type('NORMAL')  # Access only to normal user and requires to be logged in
def account():
    form = UpdateUserForm()  # Form for filling in for updating details
    if form.validate_on_submit():
        # Update the current user details with the new values
        if form.picture.data:  # If picture is being updated then run the function in picture_handler
            user_id = current_user.id
            pic = add_profile_pic(form.picture.data, user_id)
            current_user.profile_image = pic

        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone_number = form.phone_number.data
        current_user.email = form.email.data
        current_user.city = form.city.data

        db.session.commit()  # Add and commit the changes to the database
        flash('User Details Updated!', 'info')
        return redirect(url_for('users.account'))  # Reload the page after updating

    elif request.method == "GET":  # prefill the form with current details while loading the details
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone_number.data = current_user.phone_number
        form.email.data = current_user.email
        form.city.data = current_user.city

    profile_image = url_for('static',
                            filename='profile_pics/' + current_user.profile_image)  # Get the current profile image of the user

    return render_template('account.html', profile_image=profile_image, form=form)


# Wallet balance and topup history page
@users.route('/wallet')
@login_required
@check_user_type('NORMAL')  # Access only to normal user and requires to be logged in
def wallet():
    page = request.args.get('page', 1, type=int)  # filter for page number (pagenation)
    topups = TopUp.query.filter_by(user_id=current_user.id).order_by(TopUp.time.desc()).paginate(page=page,
                                                                                                 per_page=20)  # Get the topup history in desc order
    return render_template('wallet.html', user=current_user, transactions=topups)


# Wallet Balance Addition payment page
@users.route('/addbalance', methods=['GET', 'POST'])
@login_required
@check_user_type('NORMAL')  # Access only to normal user and requires to be logged in
def addbalance():
    form = AddBalanceForm()  # Form to filling in for adding wallet balance
    if form.validate_on_submit():
        current_user.add_wallet_balance(form.amount.data)
        topup = TopUp(user_id=current_user.id,
                      credit_card_number=form.card.data,
                      amount=form.amount.data)
        db.session.add_all([topup])
        db.session.commit()
        return redirect(url_for('users.wallet'))
    return render_template('addbalance.html', form=form, user=current_user)


# User Ride history table page
@users.route('/userrides')
@login_required
@check_user_type('NORMAL')  # Access only to normal user and requires to be logged in
def userrides():
    page = request.args.get('page', 1, type=int)  # filter for page number (pagenation)
    transactions = Transaction.query.filter_by(user_id=current_user.id, paid='YES').order_by(
        Transaction.time.desc()).paginate(page=page, per_page=30)  # Get past rides and their transactions
    return render_template('userrides.html', transactions=transactions)


# User review history
@users.route('/userreviews')
@login_required
@check_user_type('NORMAL')  # Access only to normal user and requires to be logged in
def userreviews():
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.reviewed_at.desc()).paginate(page=page,
                                                                                                           per_page=30)  # Get past ratings and reviews
    return render_template('userreviews.html', reviews=reviews)


# User bike report page
@users.route('/reportbike', methods=['GET', 'POST'])
@login_required
@check_user_type('NORMAL')  # Access only to normal user and requires to be logged in
def reportbike():
    form = ReportBikeForm()  # Form to filling in for reporting defective bike
    if form.validate_on_submit():  # Logic to perform after filling in the form
        repair = Repair(user_id=current_user.id, bike_number=form.bike_number.data, description=form.description.data,
                        urgency=form.urgency.data)  # Create a repair record
        bike = BikeInfo.query.filter_by(bike_number=form.bike_number.data).first()
        if not form.urgency.data == 'LOW':  # Make the bike unavailable if urgency is MEDIUM or HIGH
            bike.status = 'REPAIR'
        db.session.add_all([repair, bike])  # Add and commit the changes to the database
        db.session.commit()
        flash('Successfully Reported', 'success')
        return redirect(url_for('users.reportbike'))  # Reload the page after submitting the form
    return render_template('reportbike.html', form=form)


# User details and history page
@users.route("/user/<int:user_id>")
@login_required
@check_user_type(['OPERATOR', 'MANAGER'])  # Access only to operator and manager and requires to be logged in
def user_info(user_id):
    page = [request.args.get('p1', 1, type=int), request.args.get('p2', 1, type=int),
            request.args.get('p3', 1, type=int),
            request.args.get('p4', 1, type=int)]  # filter for page numbers for multiple tables (pagenation)
    user = User.query.filter_by(id=user_id).first_or_404()  # Check if user exists and get his details
    # Get the topup, transaction, reviews and reports history
    topups = TopUp.query.filter_by(user_id=user.id).order_by(TopUp.time.desc()).paginate(page=page[0], per_page=5)
    transactions = Transaction.query.filter_by(user_id=user.id, paid='YES').order_by(Transaction.time.desc()).paginate(
        page=page[1], per_page=10)
    reviews = Review.query.filter_by(user_id=user.id).order_by(Review.reviewed_at.desc()).paginate(page=page[2],
                                                                                                   per_page=10)
    reports = Repair.query.filter_by(user_id=user.id).order_by(Repair.created_at.desc()).paginate(page=page[3],
                                                                                                  per_page=5)
    return render_template('user_info.html', user=user, topups=topups, transactions=transactions, reviews=reviews,
                           reports=reports, p1=page[0], p2=page[1], p3=page[2], p4=page[3],
                           user_type=current_user.user_type.name)
