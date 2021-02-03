from flask import render_template,url_for,flash,redirect,request,Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from easy_ride import db
from easy_ride.models import User, LoginLog, RideLog
from easy_ride.users.forms import RegistrationForm,LoginForm,UpdateUserForm
from easy_ride.users.picture_handler import add_profile_pic

users = Blueprint('users',__name__)

#Logout
@users.route("/logout")
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


@users.route('/wallet',methods=['GET','POST'])
def wallet():
    return render_template('wallet.html')


@users.route('/userrides',methods=['GET','POST'])
def userrides():
    page = request.args.get('page', 1, type=int)
    userrides = RideLog.query.filter_by(user_id=current_user.id).order_by(RideLog.end_time.desc()).paginate(page=page, per_page=5)
    return render_template('userrides.html', userrides = userrides)
