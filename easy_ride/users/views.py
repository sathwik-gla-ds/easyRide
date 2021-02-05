from flask import render_template,url_for,flash,redirect,request,Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from easy_ride import db
from easy_ride.models import User, LoginLog, RideLog, Transaction, Review, Repair, BikeInfo
from easy_ride.users.forms import RegistrationForm,LoginForm,UpdateUserForm,AddBalanceForm,ReportBikeForm
from easy_ride.users.picture_handler import add_profile_pic

users = Blueprint('users',__name__)

#Logout
@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("core.index"))

# register
@users.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    phone_number=form.phone_number.data,
                    email=form.email.data,
                    password=form.password.data,
                    city=form.city.data,
                    user_type='NORMAL')

        db.session.add(user)
        db.session.commit()
        flash('Thank you for registering in our application!')
        return redirect(url_for('users.login'))

    return render_template('register.html',form=form)

# login
@users.route('/login',methods=['GET','POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            if user.check_password(form.password.data):
                login_user(user)
                flash('Logged in Successfully!')
                next = request.args.get('next')
                if next ==None or not next[0]=='/':
                    next = url_for('core.index')
                return redirect(next)
            else:
                flash('please enter the correct password!')
        else:
            flash('This email id is not registered with us!')
    return render_template('login.html',form=form)

# account (update UserForm)
@users.route('/account',methods=['GET','POST'])
@login_required
def account():

    form = UpdateUserForm()
    if form.validate_on_submit():

        if form.picture.data:
            user_id = current_user.id
            pic = add_profile_pic(form.picture.data,user_id)
            current_user.profile_image = pic

        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone_number = form.phone_number.data
        current_user.email = form.email.data
        current_user.city = form.city.data

        db.session.commit()
        flash('User Details Updated!')
        return redirect(url_for('users.account'))

    elif request.method == "GET":
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone_number.data = current_user.phone_number
        form.email.data = current_user.email
        form.city.data = current_user.city

    profile_image = url_for('static',filename='profile_pics/'+current_user.profile_image)
    return render_template('account.html',profile_image=profile_image,form=form)


@users.route('/wallet')
@login_required
def wallet():
    user = User.query.filter_by(id=current_user.id).first()
    return render_template('wallet.html', user=user)


@users.route('/addbalance',methods=['GET','POST'])
@login_required
def addbalance():
    form = AddBalanceForm()
    user = User.query.filter_by(id=current_user.id).first()
    if form.validate_on_submit():
        user.add_wallet_balance(form.amount.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users.wallet'))
    return render_template('addbalance.html', form=form, user=user)


@users.route('/userrides')
@login_required
def userrides():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.filter_by(user_id=current_user.id, paid='YES').order_by(Transaction.time.desc()).paginate(page=page, per_page=10)
    return render_template('userrides.html', transactions = transactions)


@users.route('/userreviews')
@login_required
def userreviews():
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.reviewed_at.desc()).paginate(page=page, per_page=10)
    return render_template('userreviews.html', reviews = reviews)


@users.route('/reportbike',methods=['GET','POST'])
@login_required
def reportbike():
    form = ReportBikeForm()
    if form.validate_on_submit():
        repair = Repair(user_id = current_user.id, bike_number = form.bike_number.data, description = form.bike_number.data, urgency=form.urgency.data)
        bike = BikeInfo.query.filter_by(bike_number=form.bike_number.data).first()
        if not form.urgency.data == 'LOW':
            bike.status = 'REPAIR'
        db.session.add_all([repair,bike])
        db.session.commit()
        flash('Successfully Reported')
        return redirect(url_for('users.reportbike'))
    return render_template('reportbike.html', form = form)
