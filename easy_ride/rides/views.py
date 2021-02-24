from flask import render_template,url_for,flash,redirect,request,Blueprint
from flask_login import current_user,login_required
from easy_ride.rides.forms import StartRideForm, StopRideForm, PaymentForm
from easy_ride.models import User, Transaction, LoginLog, BikeInfo, RideLog, Review
from datetime import datetime
from easy_ride import db
import random
from easy_ride.helpers import check_user_type

rides = Blueprint('rides', __name__)

@rides.route('/rent',methods=['GET','POST'])
@login_required
@check_user_type('NORMAL')
def rent():
    current_rides = RideLog.query.filter_by(user_id = current_user.id, current = 'YES').first()
    payment = Transaction.query.filter_by(user_id = current_user.id, paid = 'NO').first()
    if payment is None:
        if current_rides is None:
            form = StartRideForm()
            if form.validate_on_submit():
                bike = BikeInfo.query.filter_by(last_location=form.location.data, status='YES').first()
                if bike is not None:
                    ride = RideLog(user_id = current_user.id,
                                     bike_number = bike.bike_number,
                                     start_location = form.location.data,
                                     current = "YES")

                    bike.status = 'NO'
                    user = User.query.filter_by(id=current_user.id).first()
                    user.session_var = 'RENTED'
                    db.session.add_all([user, ride, bike])
                    db.session.commit()

                    return redirect(url_for('rides.booking'))
                else:
                    flash("Sorry, but no bikes are available currently at the location you choose!")
            return render_template('rent.html', form=form)
        else:
            flash("Please return the previous bike before you book another")
            return redirect(url_for('rides.placeback'))
    else:
        flash("Please pay for the previous ride before you book another")
        return redirect(url_for('rides.payment'))


@rides.route('/placeback',methods=['GET','POST'])
@login_required
@check_user_type('NORMAL')
def placeback():
    current_ride = RideLog.query.filter_by(user_id = current_user.id, current = 'YES').first()
    if current_ride is not None:
        bike = BikeInfo.query.filter_by(bike_number=current_ride.bike_number).first()
        form = StopRideForm()
        if form.validate_on_submit():
            minutes = current_ride.get_minutes(datetime.utcnow())
            amount = 1 + int(minutes*0.2)
            user = User.query.filter_by(id=current_user.id).first()

            if (form.payment_type.data == "CARD") or (form.payment_type.data == "WALLET" and user.wallet_balance > amount):
                current_ride.end_ride(form.location.data)
                bike.place_back(form.location.data)

                transaction = Transaction(user_id = current_ride.user_id,
                                           payment_type = form.payment_type.data,
                                           amount = amount,
                                           ride_id = current_ride.ride_id,
                                           paid = 'NO')
                user.session_var = 'PAYMENT'
                if form.rating.data:
                    review = Review(current_ride.user_id, current_ride.ride_id, form.rating.data, form.review.data)
                    db.session.add(review)
                db.session.add_all([current_ride, bike, transaction, user])
                db.session.commit()

                return redirect(url_for('rides.payment'))
            else:
                flash('Not enough balance in the wallet! Please choose credit card instead.')
        return render_template('placeback.html', form = form)
    else:
        return redirect(url_for('rides.rent'))


@rides.route('/booking')
@login_required
@check_user_type('NORMAL')
def booking():
    current_ride = RideLog.query.filter_by(user_id = current_user.id, current = 'YES').first()
    if current_ride is not None:
        bike = BikeInfo.query.filter_by(bike_number=current_ride.bike_number).first()
        return render_template('booking.html', bike=bike, current_ride = current_ride)
    else:
        return redirect(url_for('rides.rent'))


@rides.route('/payment',methods=['GET','POST'])
@login_required
@check_user_type('NORMAL')
def payment():
    transaction = Transaction.query.filter_by(user_id=current_user.id, paid='NO').first()
    if transaction is not None:
        user = User.query.filter_by(id=current_user.id).first()
        if transaction.payment_type.name == 'WALLET':
            user.deduct_wallat_balance(transaction.amount)
            user.session_var = ''
            transaction.update_payment()
            db.session.add_all([user, transaction])
            db.session.commit()
            return redirect(url_for('users.userrides'))
        else:
            form = PaymentForm()
            ride = RideLog.query.filter_by(ride_id = transaction.ride_id).first()
            if form.validate_on_submit():
                today = datetime.today()
                if form.year.data == '2021' and int(form.month.data)<today.month:
                    flash('The expiry date cannot be before today')
                else:
                    transaction.update_payment(form.card.data)
                    user.session_var = ''
                    db.session.add_all([user, transaction])
                    db.session.commit()
                    return redirect(url_for('users.userrides'))
            return render_template('payment.html', form = form, transaction = transaction, ride = ride, time = ride.get_minutes(ride.end_time))
    else:
        flash('No pending payments')
        return redirect(url_for('rides.rent'))
