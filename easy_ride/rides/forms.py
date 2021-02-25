# contains the forms related to ride pages such as renting, returning, payment

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField, TextAreaField
from wtforms.validators import DataRequired
from wtforms import ValidationError


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


# Form to fill in information used by the user to rent and start a ride
class StartRideForm(FlaskForm):
    # Fields in form to fill
    location = SelectField('Start location', validators=[DataRequired()], choices=[('HILLHEAD', 'Hillhead'), ('PARTICK', 'Partick'), ('FINNIESTON', 'Finnieston'), ('GOVAN', 'Govan'), ('LAURIESTON', 'Laurieston')], render_kw={'class':'form-select', 'placeholder':' '})
    submit = SubmitField('Book', render_kw={'class':'btn btn-primary'})

# Form to fill in information used by the user to end an ongoing ride
class StopRideForm(FlaskForm):
    # Fields in form to fill
    location = SelectField('End location', validators=[DataRequired()], choices=[('HILLHEAD', 'Hillhead'), ('PARTICK', 'Partick'), ('FINNIESTON', 'Finnieston'), ('GOVAN', 'Govan'), ('LAURIESTON', 'Laurieston')], render_kw={'class':'form-select', 'placeholder':' '})
    payment_type = RadioField('Payment with: ', validators=[DataRequired()], choices=["CARD", "WALLET"])
    rating = RadioField('Rating: ', choices=[5, 4, 3, 2, 1])
    review = TextAreaField('Comments', render_kw={'class':'form-control', 'placeholder':' '})
    submit = SubmitField('End ride', render_kw={'class':'btn btn-primary'})

# Form to fill in information used by the user to pay for the ride using credit card
class PaymentForm(FlaskForm):
    # Validation functions to check if the card number entered is in the correct format
    def check_card_number(self, field):
        if field.data.isdigit():
            if int(field.data) > 9999999999999999 or int(field.data) < 1000000000000000:
                raise ValidationError('Your credit card number is not valid.')
        else:
            raise ValidationError('Your credit card number is not valid.')
    # Validation functions to check if the security number entered is in the correct format
    def check_cvv_number(self, field):
        if int(field.data) >999 or int(field.data) <100:
            raise ValidationError('Invalid security code')

    # Fields in form to fill
    name = StringField('Name on the card', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    card = StringField('Credit Card Number', validators=[DataRequired(), check_card_number], render_kw={'class':'form-control', 'placeholder':' '})
    month = SelectField('Expiry', validators=[DataRequired()], choices=[('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], render_kw={'class':'form-select', 'placeholder':' '})
    year = SelectField('Expiry', validators=[DataRequired()], choices=['2021', '2022','2023', '2024','2025', '2026','2027', '2028','2029','2030'], render_kw={'class':'form-select', 'placeholder':' '})
    cvv = StringField('Security Code', validators=[DataRequired(), check_cvv_number], render_kw={'class':'form-control', 'placeholder':' '})
    submit = SubmitField('Pay', render_kw={'class':'btn btn-primary'})
