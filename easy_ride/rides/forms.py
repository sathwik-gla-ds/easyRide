from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, RadioField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed
from datetime import datetime


class StartRideForm(FlaskForm):
    location = SelectField('Start location', validators=[DataRequired()], choices=[('HILLHEAD', 'Hillhead'), ('PARTICK', 'Partick'), ('FINNIESTON', 'Finnieston'), ('GOVAN', 'Govan'), ('LAURIESTON', 'Laurieston')], render_kw={'class':'form-select', 'placeholder':' '})
    submit = SubmitField('Book', render_kw={'class':'btn btn-primary'})

class StopRideForm(FlaskForm):
    location = SelectField('End location', validators=[DataRequired()], choices=[('HILLHEAD', 'Hillhead'), ('PARTICK', 'Partick'), ('FINNIESTON', 'Finnieston'), ('GOVAN', 'Govan'), ('LAURIESTON', 'Laurieston')], render_kw={'class':'form-select', 'placeholder':' '})
    payment_type = RadioField('Payment with: ', validators=[DataRequired()], choices=["CARD", "WALLET"])
    rating = RadioField('Rating: ', choices=[5, 4, 3, 2, 1])
    review = TextAreaField('Comments', render_kw={'class':'form-control', 'placeholder':' '})
    submit = SubmitField('End ride', render_kw={'class':'btn btn-primary'})

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
    name = StringField('Name on the card', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    card = StringField('Credit Card Number', validators=[DataRequired(), check_card_number], render_kw={'class':'form-control', 'placeholder':' '})
    month = SelectField('Expiry', validators=[DataRequired()], choices=[('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], render_kw={'class':'form-select', 'placeholder':' '})
    year = SelectField('Expiry', validators=[DataRequired()], choices=['2021', '2022','2023', '2024','2025', '2026','2027', '2028','2029','2030'], render_kw={'class':'form-select', 'placeholder':' '})
    cvv = StringField('Security Code', validators=[DataRequired(), check_cvv_number], render_kw={'class':'form-control', 'placeholder':' '})
    submit = SubmitField('Pay', render_kw={'class':'btn btn-primary'})
