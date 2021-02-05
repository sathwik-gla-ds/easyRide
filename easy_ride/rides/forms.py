from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, RadioField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from datetime import datetime


class StartRideForm(FlaskForm):
    location = SelectField('Start location', validators=[DataRequired()], choices=['HILLHEAD', 'PARTICK', 'FINNIESTON', 'GOVAN', 'LAURIESTON'])
    submit = SubmitField('Book')

class StopRideForm(FlaskForm):
    location = SelectField('End location', validators=[DataRequired()], choices=['HILLHEAD', 'PARTICK', 'FINNIESTON', 'GOVAN', 'LAURIESTON'])
    payment_type = RadioField('Payment with: ', validators=[DataRequired()], choices=["Credit Card", "Wallet"])
    rating = SelectField('Rating: ', choices=[5, 4, 3, 2, 1])
    review = TextAreaField('Comments')
    submit = SubmitField('End ride')

class PaymentForm(FlaskForm):
    def check_card_number(self, field):
        if field.data.isdigit():
            if int(field.data) > 9999999999999999 or int(field.data) < 1000000000000000:
                raise ValidationError('Your credit card number is not valid.')
        else:
            raise ValidationError('Your credit card number is not valid.')
    def check_cvv_number(self, field):
        if int(field.data) >999 or int(field.data) <100:
            raise ValidationError('Invalid security code')
    name = StringField('Name on the card', validators=[DataRequired()])
    card = StringField('Credit Card Number', validators=[DataRequired(), check_card_number])
    month = SelectField('Expiry', validators=[DataRequired()], choices=['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])
    year = SelectField('Expiry', validators=[DataRequired()], choices=['2021', '2022','2023', '2024','2025', '2026','2027', '2028','2029','2030'])
    cvv = StringField('Security Code', validators=[DataRequired(), check_cvv_number])
    submit = SubmitField('Pay')
