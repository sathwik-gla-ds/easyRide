from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed


class StartRideForm(FlaskForm):
    location = StringField('Start location', validators=[DataRequired()])
    submit = SubmitField('Book')

class StopRideForm(FlaskForm):
    location = StringField('End location', validators=[DataRequired()])
    payment_type = RadioField('Payment with: ', validators=[DataRequired()], choices=["Credit Card", "Wallet"])
    submit = SubmitField('End ride')
