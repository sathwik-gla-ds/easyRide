from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed

from flask_login import current_user
from easy_ride.models import User, BikeInfo

class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    def check_email_reg(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has already been registered.')

    def check_phone_reg(self, field):
        if User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('Your phone number has already been registered.')

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = IntegerField('Phone Number', validators=[DataRequired(), check_phone_reg])
    email = StringField('Email', validators = [DataRequired(), Email(), check_email_reg])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password',message='passwords do not match!')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    city = SelectField('City', choices=['GLASGOW'], validators=[DataRequired()])
    submit = SubmitField('Register')

class UpdateUserForm(FlaskForm):
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg','png','jpeg'])])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = IntegerField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators = [DataRequired(), Email()])
    city = SelectField('City', choices=['Glasgow'], validators=[DataRequired()])
    submit = SubmitField('Update Details')

class AddBalanceForm(FlaskForm):
    def check_card_number(self, field):
        if field.data.isdigit():
            if int(field.data) > 9999999999999999 or int(field.data) < 1000000000000000:
                raise ValidationError('Your credit card number is not valid.')
        else:
            raise ValidationError('Your credit card number is not valid.')
    def check_cvv_number(self, field):
        if int(field.data) >999 or int(field.data) <100:
            raise ValidationError('Invalid security code')

    amount = IntegerField('Amount to add', validators=[DataRequired()])
    name = StringField('Name on the card', validators=[DataRequired()])
    card = StringField('Credit Card Number', validators=[DataRequired(), check_card_number])
    month = SelectField('Expiry', validators=[DataRequired()], choices=['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'], render_kw={'class':'form-select'})
    year = SelectField('Expiry', validators=[DataRequired()], choices=['2021', '2022','2023', '2024','2025', '2026','2027', '2028','2029','2030'], render_kw={'class':'form-select'})
    cvv = StringField('Security Code', validators=[DataRequired(), check_cvv_number])
    submit = SubmitField('Pay')

class ReportBikeForm(FlaskForm):
    def bike_num_check(self, field):
        if not BikeInfo.query.filter_by(bike_number=field.data).first():
            raise ValidationError('No bike found with the given number')

    bike_number = IntegerField('Bike Number', validators=[DataRequired(), bike_num_check])
    description = TextAreaField('Description', validators=[DataRequired()])
    urgency = SelectField('Level of priority', validators=[DataRequired()], choices=['LOW', 'MEDIUM', 'HIGH'])
    submit = SubmitField('Submit')
