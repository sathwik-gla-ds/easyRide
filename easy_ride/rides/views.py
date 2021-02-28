# contains the routes related to ride pages such as renting, returning, payment

from flask import render_template,url_for,flash,redirect,request,Blueprint
from flask_login import current_user,login_required
from easy_ride.rides.forms import StartRideForm, StopRideForm, PaymentForm
from easy_ride.models import User, Transaction, LoginLog, BikeInfo, RideLog, Review
from datetime import datetime
from easy_ride import db
from easy_ride.helpers import check_user_type


rides = Blueprint('rides', __name__) # For registering the Blueprint/folder in main __init__.py file


# Page for renting the bike
@rides.route('/rent',methods=['GET','POST'])
@login_required
@check_user_type('NORMAL') # Access only to normal user and requires to be logged in
def rent():
    # Check if there are any on-going rides or pending payments for the user before loading the page. If there are redirect appropriately.
    current_rides = RideLog.query.filter_by(user_id = current_user.id, current = 'YES').first()
    payment = Transaction.query.filter_by(user_id = current_user.id, paid = 'NO').first()
    if payment is None:
        if current_rides is None:
            form = StartRideForm() # Form to fill for renting a bike
            if form.validate_on_submit(): # Logic to perform after submitting the form
                bike = BikeInfo.query.filter_by(last_location=form.location.data, status='YES').first() # Check if any bikes are available at the selected location

                if bike is not None:
                    ride = RideLog(user_id = current_user.id,
                                    bike_number = bike.bike_number,
                                    start_location = form.location.data,
                                    current = "YES") # Create a new ride log
                    bike.status = 'NO' # Update the bike status
                    current_user.session_var = 'RENTED' # Update the session variable so that we will only show option to return instead of rent in the navbar
                    db.session.add_all([ride, bike]) # Add and update the changes to the database
                    db.session.commit()
                    return redirect(url_for('rides.booking')) # Redirect to the booking the page after user submits the form
                else:
                    flash("Sorry, but no bikes are available currently at the location you choose!", "warning")

            return render_template('rent.html', form=form) # Loads the rent page if there are no pending payments or on-going rides
        else: # Redirect to payments page if there are pending payments
            flash("Please return the previous bike before you book another", "warning")
            return redirect(url_for('rides.placeback'))
    else: # Redirect to payments page if there are any on going
        flash("Please pay for the previous ride before you book another", "warning")
        return redirect(url_for('rides.payment'))


# Page for returning the bike
@rides.route('/placeback',methods=['GET','POST'])
@login_required
@check_user_type('NORMAL') # Access only to normal user and requires to be logged in
def placeback():
    current_ride = RideLog.query.filter_by(user_id = current_user.id, current = 'YES').first() #Check if the user has any ongoing ride first  before loading the page
    if current_ride is not None:
        bike = BikeInfo.query.filter_by(bike_number=current_ride.bike_number).first()
        form = StopRideForm() # Form to fill in for ending the ride

        if form.validate_on_submit(): # Logic to perform after filling in the form
            minutes = current_ride.get_minutes(datetime.utcnow()) # Get the time of the ride and calculate the amount required
            amount = 1 + int(minutes*0.2)

            # Only allow to proceed to payment if a user choose to pay with card or has enough balance in the wallet to pay
            if (form.payment_type.data == "CARD") or (form.payment_type.data == "WALLET" and current_user.wallet_balance > amount):
                current_ride.end_ride(form.location.data) #Update the ride log and bike location and status
                bike.place_back(form.location.data)
                transaction = Transaction(user_id = current_ride.user_id,
                                           payment_type = form.payment_type.data,
                                           amount = amount,
                                           ride_id = current_ride.ride_id,
                                           paid = 'NO') # create a new transaction record
                current_user.session_var = 'PAYMENT' # Update the session variable so that we will only show option payment instead of rent or return in the navbar
                if form.rating.data: # Create rating record if user has rated the ride
                    review = Review(current_ride.user_id, current_ride.ride_id, form.rating.data, form.review.data)
                    db.session.add(review)
                db.session.add_all([current_ride, bike, transaction])  # Add and update the changes to the database
                db.session.commit()

                return redirect(url_for('rides.payment')) # Redirect to payment page after ending the ride
            else: # Ask user to choose to pay with card if there is not enough balance in the wallet
                flash('Not enough balance in the wallet! Please choose credit card instead.', 'warning')
        return render_template('placeback.html', form = form)
    else: # Redirect to rent page if user has no ongoing rides
        return redirect(url_for('rides.rent'))


# Page for showing booking details to the user
@rides.route('/booking')
@login_required
@check_user_type('NORMAL') # Access only to normal user and requires to be logged in
def booking():
    current_ride = RideLog.query.filter_by(user_id = current_user.id, current = 'YES').first() # Check if user has any on-going rides before loading the page
    if current_ride is not None:
        bike = BikeInfo.query.filter_by(bike_number=current_ride.bike_number).first()
        return render_template('booking.html', bike=bike, current_ride = current_ride)
    else: # Redirect to rent page if user has no ongoing rides
        return redirect(url_for('rides.rent'))


# Page for payment
@rides.route('/payment',methods=['GET','POST'])
@login_required
@check_user_type('NORMAL') # Access only to normal user and requires to be logged in
def payment():
    transaction = Transaction.query.filter_by(user_id=current_user.id, paid='NO').first() # Check if user has any pending payments before loading the page
    if transaction is not None:
        if transaction.payment_type.name == 'WALLET': #Deduct balance from wallet if choosen to pay with wallet
            current_user.deduct_wallat_balance(transaction.amount)
            current_user.session_var = '' # Update the session variable so that we will only show option rent instead of payment or return in the navbar
            transaction.update_payment() # Update the transaction
            db.session.add_all([transaction]) #Add records and update the database
            db.session.commit()
            return redirect(url_for('users.userrides')) # Since choosed to pay with wallet skip loading this page and redirect to the ride history page
        else:
            form = PaymentForm() # Payment form to fill in case choose to pay with the card
            ride = RideLog.query.filter_by(ride_id = transaction.ride_id).first()
            if form.validate_on_submit(): # Logic to perform when the form is filled
                today = datetime.today()
                if form.year.data == '2021' and int(form.month.data)<today.month: # Check if the expiry date is valid
                    flash('The expiry date cannot be before today', 'warning')
                else:
                    transaction.update_payment(form.card.data) # Update the transaction
                    current_user.session_var = ''
                    db.session.add_all([transaction]) #Add records and update the database
                    db.session.commit()
                    return redirect(url_for('users.userrides'))
            return render_template('payment.html', form = form, transaction = transaction, ride = ride, time = ride.get_minutes(ride.end_time))
    else: # If there are no pending payments redirect to the rent page instead
        flash('No pending payments', 'info')
        return redirect(url_for('rides.rent'))
