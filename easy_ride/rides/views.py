from flask import render_template,url_for,flash,redirect,request,Blueprint
from flask_login import current_user,login_required
from easy_ride.rides.forms import StartRideForm, StopRideForm
from easy_ride.models import User, Transaction, LoginLog, BikeInfo, StartRide, RideLog
from datetime import datetime
from easy_ride import db
import random

rides = Blueprint('rides', __name__)

@rides.route('/rent',methods=['GET','POST'])
def rent():
    form = StartRideForm()

    if form.validate_on_submit():
        # current_rides = StartRide.query.filter_by(user_id = current_user.id)
        # if current_rides is None:
        bike = BikeInfo.query.filter_by(last_location=form.location.data, status='YES').first()

        if bike is not None:
            ride = StartRide(user_id = current_user.id,
                             bike_number = bike.bike_number,
                             start_location = form.location.data)

            bike.status = 'NO'
            db.session.add(ride)
            db.session.add(bike)
            db.session.commit()

            return redirect(url_for('rides.booking'))
        else:
            return redirect(url_for('rides.notavailable'))
        # else:
        #     flash("Please return the previous bike before you book another")
        #     return redirect(url_for('rides.placeback'))
    return render_template('rent.html', form=form)

@rides.route('/placeback',methods=['GET','POST'])
def placeback():
    # current_ride = StartRide.query.filter_by(user_id = current_user.id).first()
    # if current_ride is not None:
    #     bike = BikeInfo.query.filter_by(bike_number=current_ride.bike_number).first()
    #     form = StopRideForm()
    #     if form.validate_on_submit():
    #         time_delta = (datetime.utcnow() - current_ride.start_location)
    #         total_seconds = time_delta.total_seconds()
    #         minutes = total_seconds/60
    #         amount = minutes*0.2
    #         user = User.query.filter_by(id=current_user.id)
    #
    #         if (form.payment_type.data == "Credit Card") or (form.payment_type.data == "Wallet" and user.wallet > amount):
    #             ride = RideLog(ride_id=current_ride.ride_id,
    #                            user_id=current_ride.user_id,
    #                            bike_number=current_ride.bike_number,
    #                            start_location=current_ride.start_location,
    #                            end_location=form.location.data,
    #                            start_time=current_ride.start_time)
    #
    #             bike.bike_pin = random.randint(1000,9999)
    #
    #             transactions = Transaction(user_id = current_ride.ride_id,
    #                                        payment_type = ,
    #                                        credit_card_number,
    #                                        amount,
    #                                        ride_id,
    #                                        paid)
    #
    #
    #
    #
    #
    #     return render_template('placeback.html', form = form)
    # else:
    #     return redirect(url_for('rides.rent'))
    return render_template('placeback.html')

@rides.route('/booking')
def booking():
    current_ride = StartRide.query.filter_by(user_id = current_user.id).first()
    if current_ride is not None:
        bike = BikeInfo.query.filter_by(bike_number=current_ride.bike_number).first()
        return render_template('booking.html', bike=bike, current_ride = current_ride)
    else:
        return redirect(url_for('rides.rent'))

@rides.route('/notavailable')
def notavailable():
    return render_template('notavailable.html')
