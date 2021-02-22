from flask import render_template,url_for,flash,redirect,request,Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from easy_ride import db
from easy_ride.models import User, LoginLog, RideLog, Transaction, Review, Repair, BikeInfo, TopUp
from easy_ride.users.forms import RegistrationForm,LoginForm,UpdateUserForm,AddBalanceForm,ReportBikeForm
from easy_ride.users.picture_handler import add_profile_pic
from easy_ride.helpers import check_user_type


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
    if current_user.is_authenticated:
        logout_user()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower(), user_status='NORMAL').first()
        if user is not None:
            if user.check_password(form.password.data):
                login_user(user)
                flash('Logged in Successfully!')
                login_log = LoginLog(user.id, user.user_type.name)
                db.session.add(login_log)
                db.session.commit()
                next = request.args.get('next')
                if next ==None or not next[0]=='/':
                    if user.user_type.name == 'NORMAL':
                        next = url_for('core.index')
                    elif user.user_type.name == 'OPERATOR':
                        next = url_for('employees.operator_view')
                    else:
                        next = url_for('employees.manager_view')
                return redirect(next)
            else:
                flash('please enter the correct password!')
        else:
            flash('This email id is not registered with us!')
    return render_template('login.html',form=form)


# account (update UserForm)
@users.route('/account',methods=['GET','POST'])
@login_required
@check_user_type('NORMAL')
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
@check_user_type('NORMAL')
def wallet():
    user = User.query.filter_by(id=current_user.id).first()
    page = request.args.get('page', 1, type=int)
    topups = TopUp.query.filter_by(user_id=current_user.id).order_by(TopUp.time.desc()).paginate(page=page, per_page=10)
    return render_template('wallet.html', user=user, transactions = topups)


@users.route('/addbalance',methods=['GET','POST'])
@login_required
@check_user_type('NORMAL')
def addbalance():
    form = AddBalanceForm()
    user = User.query.filter_by(id=current_user.id).first()
    if form.validate_on_submit():
        user.add_wallet_balance(form.amount.data)
        topup = TopUp(user_id = user.id,
                       credit_card_number = form.card.data,
                       amount = form.amount.data)
        db.session.add_all([user,topup])
        db.session.commit()
        return redirect(url_for('users.wallet'))
    return render_template('addbalance.html', form=form, user=user)


@users.route('/userrides')
@login_required
@check_user_type('NORMAL')
def userrides():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.filter_by(user_id=current_user.id, paid='YES').order_by(Transaction.time.desc()).paginate(page=page, per_page=10)
    return render_template('userrides.html', transactions = transactions)


@users.route('/userreviews')
@login_required
@check_user_type('NORMAL')
def userreviews():
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.reviewed_at.desc()).paginate(page=page, per_page=10)
    return render_template('userreviews.html', reviews = reviews)

@users.route('/reportbike',methods=['GET','POST'])
@login_required
@check_user_type('NORMAL')
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


@users.route("/user/<int:user_id>")
@login_required
@check_user_type(['OPERATOR', 'MANAGER'])
def user_info(user_id):
    page = [request.args.get('p1', 1, type=int), request.args.get('p2', 1, type=int), request.args.get('p3', 1, type=int), request.args.get('p4', 1, type=int)]
    user = User.query.filter_by(id=user_id).first_or_404()
    topups = TopUp.query.filter_by(user_id=user.id).order_by(TopUp.time.desc()).paginate(page=page[0], per_page=5)
    transactions = Transaction.query.filter_by(user_id=user.id, paid='YES').order_by(Transaction.time.desc()).paginate(page=page[1], per_page=5)
    reviews = Review.query.filter_by(user_id=user.id).order_by(Review.reviewed_at.desc()).paginate(page=page[2], per_page=5)
    reports = Repair.query.filter_by(user_id=user.id).order_by(Repair.created_at.desc()).paginate(page=page[3], per_page=5)
    return render_template('user_info.html', user=user, topups=topups, transactions=transactions, reviews=reviews, reports=reports, p1=page[0], p2=page[1], p3=page[2], p4=page[3], user_type = current_user.user_type.name)
