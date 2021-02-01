from flask import render_template,url_for,flash,redirect,request,Blueprint
from flask_login import current_user,login_required
from easy_ride.rides.forms import StartRideForm, StopRideForm
from easy_ride.models import User, Transaction, LoginLog, BikeInfo, RideLog
from datetime import datetime
from easy_ride import db
import random

rides = Blueprint('rides', __name__)

@rides.route('/rent',methods=['GET','POST'])
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
                    db.session.add(user)
                    db.session.add(ride)
                    db.session.add(bike)
                    db.session.commit()

                    return redirect(url_for('rides.booking'))
                else:
                    flash("Sorry, but no bikes are available currently at the location you choose!")
                    return redirect(url_for('rides.rent'))
            return render_template('rent.html', form=form)
        else:
            flash("Please return the previous bike before you book another")
            return redirect(url_for('rides.placeback'))
    else:
        flash("Please pay for the previous ride before you book another")
        return redirect(url_for('rides.payment'))

@rides.route('/placeback',methods=['GET','POST'])
def placeback():
    current_ride = RideLog.query.filter_by(user_id = current_user.id, current = 'YES').first()
    if current_ride is not None:
        bike = BikeInfo.query.filter_by(bike_number=current_ride.bike_number).first()
        form = StopRideForm()
        if form.validate_on_submit():
            time_delta = (datetime.utcnow() - current_ride.start_time)
            total_seconds = time_delta.total_seconds()
            minutes = total_seconds/60
            amount = minutes*0.2
            user = User.query.filter_by(id=current_user.id).first()

            if (form.payment_type.data == "Credit Card") or (form.payment_type.data == "Wallet" and user.wallet_balance > amount):
                current_ride.end_location = form.location.data
                current_ride.end_time = datetime.utcnow()
                current_ride.current = 'NO'

                bike.bike_pin = random.randint(1000,9999)
                bike.last_location = form.location.data
                bike.status = 'YES'

                if form.payment_type.data == "Credit Card":
                    payment_type = 'CARD'
                else:
                    payment_type = 'WALLET'

                transaction = Transaction(user_id = current_ride.user_id,
                                           payment_type = payment_type,
                                           amount = amount,
                                           ride_id = current_ride.ride_id,
                                           paid = 'NO')
                user.session_var = 'PAYMENT'
                db.session.add(current_ride)
                db.session.add(bike)
                db.session.add(transaction)
                db.session.commit()

                return redirect(url_for('rides.payment'))
            else:
                flash('Not enough balance in the wallet! Please choose credit card instead.')
        return render_template('placeback.html', form = form)
    else:
        return redirect(url_for('rides.rent'))

@rides.route('/booking')
def booking():
    current_ride = RideLog.query.filter_by(user_id = current_user.id, current = 'YES').first()
    if current_ride is not None:
        bike = BikeInfo.query.filter_by(bike_number=current_ride.bike_number).first()
        return render_template('booking.html', bike=bike, current_ride = current_ride)
    else:
        return redirect(url_for('rides.rent'))

@rides.route('/notavailable')
def notavailable():
    return render_template('notavailable.html')

@rides.route('/payment')
def payment():
    return render_template('payment.html')
