from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed

from flask_login import current_user
from easy_ride.models import User, BikeInfo

class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()], render_kw={'class':'form-control', 'placeholder':' '})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    submit = SubmitField('Log In', render_kw={'class':'btn btn-outline-primary'})

class RegistrationForm(FlaskForm):
    def check_email_reg(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('This email has already been registered.')

    def check_phone_reg(self, field):
        if User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('This phone number has already been registered.')

    def check_password_reg(self, field):
        if len(field.data) < 8:
            raise ValidationError('Your password should be 8 characters or longer!')

    first_name = StringField('First Name', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    last_name = StringField('Last Name', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    phone_number = IntegerField('Phone Number', validators=[DataRequired(), check_phone_reg], render_kw={'class':'form-control', 'placeholder':' '})
    email = StringField('Email', validators = [DataRequired(), Email(), check_email_reg], render_kw={'class':'form-control', 'placeholder':' '})
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password',message='passwords do not match!'), check_password_reg], render_kw={'class':'form-control', 'placeholder':' '})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    city = SelectField('City', choices=[('GLASGOW', 'Glasgow')], validators=[DataRequired()], render_kw={'class':'form-select', 'placeholder':' '})
    submit = SubmitField('Register', render_kw={'class':'btn btn-outline-success'})

class UpdateUserForm(FlaskForm):
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg','png','jpeg'])])
    first_name = StringField('First Name', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    last_name = StringField('Last Name', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    phone_number = IntegerField('Phone Number', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    email = StringField('Email', validators = [DataRequired(), Email()], render_kw={'class':'form-control', 'placeholder':' '})
    city = SelectField('City', choices=['Glasgow'], validators=[DataRequired()], render_kw={'class':'form-select', 'placeholder':' '})
    submit = SubmitField('Update Details', render_kw={'class':'btn btn-outline-primary'})

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

    amount = IntegerField('Amount to add', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    name = StringField('Name on the card', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    card = StringField('Credit Card Number', validators=[DataRequired(), check_card_number], render_kw={'class':'form-control', 'placeholder':' '})
    month = SelectField('Month', validators=[DataRequired()], choices=[('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], render_kw={'class':'form-select', 'placeholder':' '})
    year = SelectField('Year', validators=[DataRequired()], choices=['2021', '2022','2023', '2024','2025', '2026','2027', '2028','2029','2030'], render_kw={'class':'form-select', 'placeholder':' '})
    cvv = StringField('Security Code', validators=[DataRequired(), check_cvv_number], render_kw={'class':'form-control', 'placeholder':' '})
    submit = SubmitField('Pay', render_kw={'class':'btn btn-primary'})

class ReportBikeForm(FlaskForm):
    def bike_num_check(self, field):
        if not BikeInfo.query.filter_by(bike_number=field.data).first():
            raise ValidationError('No bike found with the given number')

    bike_number = IntegerField('Bike Number', validators=[DataRequired(), bike_num_check], render_kw={'class':'form-control', 'placeholder':' '})
    description = TextAreaField('Description', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    urgency = SelectField('Level of priority', validators=[DataRequired()], choices=[('LOW', "Low"), ('MEDIUM', 'Medium'), ('HIGH', 'High')], render_kw={'class':'form-select', 'placeholder':' '})
    submit = SubmitField('Submit', render_kw={'class':'btn btn-primary'})
