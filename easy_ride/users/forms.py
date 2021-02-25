# contains the forms related to user account pages such as profile update, adding balance, reporting defective bike

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from easy_ride.models import User, BikeInfo


#================================================#
# Bootstrap classses for form fields (Reference) #
#================================================#
#{'class':'form-control'} - for all normal fields with default size
#{'class':'form-control form-control-lg'} - for all normal fields with large size
#{'class':'form-control form-control-sm'} - for all normal fields with small size
#{'class':'form-check-input'} - for all radio fields
#{'class':'form-select'} - for all select fields
#{'class':'btn btn-primary'} - for all buttons
#================================================#


# Form to fill in information used by the users to log into the application
class LoginForm(FlaskForm):
    # Fields in form to fill
    email = StringField('Email', validators = [DataRequired(), Email()], render_kw={'class':'form-control', 'placeholder':' '})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    submit = SubmitField('Log In', render_kw={'class':'btn btn-outline-primary'})

# Form to fill in information used by the normal users to register
class RegistrationForm(FlaskForm):
    # Validation functions to check if the email is already registered
    def check_email_reg(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('This email has already been registered.')
    # Validation functions to check if the phone number is already registered
    def check_phone_reg(self, field):
        if User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('This phone number has already been registered.')
    # Validation functions to check if the password is atleast 8 chars long
    def check_password_reg(self, field):
        if len(field.data) < 8:
            raise ValidationError('Your password should be 8 characters or longer!')

    # Fields in form to fill
    first_name = StringField('First Name', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    last_name = StringField('Last Name', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    phone_number = IntegerField('Phone Number', validators=[DataRequired(), check_phone_reg], render_kw={'class':'form-control', 'placeholder':' '})
    email = StringField('Email', validators = [DataRequired(), Email(), check_email_reg], render_kw={'class':'form-control', 'placeholder':' '})
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password',message='passwords do not match!'), check_password_reg], render_kw={'class':'form-control', 'placeholder':' '})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    city = SelectField('City', choices=[('GLASGOW', 'Glasgow')], validators=[DataRequired()], render_kw={'class':'form-select', 'placeholder':' '})
    submit = SubmitField('Register', render_kw={'class':'btn btn-outline-success'})

# Form to fill in information used by the users to update their profile information
class UpdateUserForm(FlaskForm):
    # Fields in form to fill
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg','png','jpeg'])])
    first_name = StringField('First Name', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    last_name = StringField('Last Name', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    phone_number = IntegerField('Phone Number', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    email = StringField('Email', validators = [DataRequired(), Email()], render_kw={'class':'form-control', 'placeholder':' '})
    city = SelectField('City', choices=['Glasgow'], validators=[DataRequired()], render_kw={'class':'form-select', 'placeholder':' '})
    submit = SubmitField('Update Details', render_kw={'class':'btn btn-outline-primary'})

# Form to fill in information used by the users to add wallet balance
class AddBalanceForm(FlaskForm):
    # Validation functions to check if card number is of 16 digits
    def check_card_number(self, field):
        if field.data.isdigit():
            if int(field.data) > 9999999999999999 or int(field.data) < 1000000000000000:
                raise ValidationError('Your credit card number is not valid.')
        else:
            raise ValidationError('Your credit card number is not valid.')
    # Validation functions to check if security code is 3 digits long
    def check_cvv_number(self, field):
        if int(field.data) >999 or int(field.data) <100:
            raise ValidationError('Invalid security code')

    # Fields in form to fill
    amount = IntegerField('Amount to add', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    name = StringField('Name on the card', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    card = StringField('Credit Card Number', validators=[DataRequired(), check_card_number], render_kw={'class':'form-control', 'placeholder':' '})
    month = SelectField('Month', validators=[DataRequired()], choices=[('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], render_kw={'class':'form-select', 'placeholder':' '})
    year = SelectField('Year', validators=[DataRequired()], choices=['2021', '2022','2023', '2024','2025', '2026','2027', '2028','2029','2030'], render_kw={'class':'form-select', 'placeholder':' '})
    cvv = StringField('Security Code', validators=[DataRequired(), check_cvv_number], render_kw={'class':'form-control', 'placeholder':' '})
    submit = SubmitField('Pay', render_kw={'class':'btn btn-primary'})

# Form to fill in information used by the users to report any defective bikes
class ReportBikeForm(FlaskForm):
    def bike_num_check(self, field):
        if not BikeInfo.query.filter_by(bike_number=field.data).first():
            raise ValidationError('No bike found with the given number')

    # Fields in form to fill
    bike_number = IntegerField('Bike Number', validators=[DataRequired(), bike_num_check], render_kw={'class':'form-control', 'placeholder':' '})
    description = TextAreaField('Description', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    urgency = SelectField('Level of priority', validators=[DataRequired()], choices=[('LOW', "Low"), ('MEDIUM', 'Medium'), ('HIGH', 'High')], render_kw={'class':'form-select', 'placeholder':' '})
    submit = SubmitField('Submit', render_kw={'class':'btn btn-primary'})
