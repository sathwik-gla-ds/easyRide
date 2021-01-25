from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed

from flask_login import current_user
from easy_ride.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = IntegerField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password',message='passwords do not match!')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    city = SelectField('City', choices=['GLASGOW'], validators=[DataRequired()])
    submit = SubmitField('Register')

    def check_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has already been registered.')

    def check_phone(self, field):
        if User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('Your phone number has already been registered.')

class UpdateUserForm(FlaskForm):
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg','png'])])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = IntegerField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators = [DataRequired(), Email()])
    city = SelectField('City', choices=['Glasgow'], validators=[DataRequired()])
    submit = SubmitField('Update Details')
