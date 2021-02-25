# contains the forms related to employees pages such as operator and manager dashboards, bikes info, rides info etc

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from easy_ride.models import User, BikeInfo, Repair


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


# Form to fill in information used by the operator to move bikes
class MoveBikeForm(FlaskForm):
    # Validation functions to check if the operator entered the correct bike number
    def bike_move_check(self, field):
        bike = BikeInfo.query.filter_by(bike_number=field.data).first()
        if not bike:
            raise ValidationError('No bike found with the given number')
        else:
            if not bike.status.name == 'YES':
                  raise ValidationError('Bike not available to move' )

    # Fields in form to fill
    bike_number = IntegerField('Bike Number', validators=[DataRequired(), bike_move_check], render_kw={'class':'form-control', 'placeholder':' '})
    new_location = SelectField('Moved location', validators=[DataRequired()], choices=['HILLHEAD', 'PARTICK', 'FINNIESTON', 'GOVAN', 'LAURIESTON'], render_kw={'class':'form-select', 'placeholder':' '})
    submit = SubmitField('Change Location', render_kw={'class':'btn btn-primary'})

# Form to fill in information used by the
class RepairBikeForm(FlaskForm):
    # Validation functions to check if bike is available to repair
    def bike_repair_check(self, field):
        if not Repair.query.filter_by(bike_number=field.data, repair_status='NO').first():
            raise ValidationError('No bike reported with the given number')
        else:
            if BikeInfo.query.filter_by(bike_number=field.data).first().status.name not in ['YES', 'REPAIR']:
                raise ValidationError('Bike currently not available')

    # Fields in form to fill
    bike_number = IntegerField('Bike Number', validators=[DataRequired(), bike_repair_check], render_kw={'class':'form-control', 'placeholder':' '})
    level_of_repair = SelectField('Level of repair', validators=[DataRequired()], choices=[0, 1, 2, 3, 4, 5], render_kw={'class':'form-select', 'placeholder':' '})
    comment = TextAreaField('Comment', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    submit = SubmitField('Complete Repair', render_kw={'class':'btn btn-primary'})

# Form to fill in information used by the
class AddOperatorForm(FlaskForm):
    # Validation functions to check if email entered is already registered or not
    def check_email_reg(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('This email has already been registered.')
    # Validation functions to check if phone number entered is already registered or not
    def check_phone_reg(self, field):
        if User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('This phone number has already been registered.')

    # Fields in form to fill
    first_name = StringField('First Name', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    last_name = StringField('Last Name', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    phone_number = IntegerField('Phone Number', validators=[DataRequired(), check_phone_reg], render_kw={'class':'form-control', 'placeholder':' '})
    email = StringField('Email', validators = [DataRequired(), Email(), check_email_reg], render_kw={'class':'form-control', 'placeholder':' '})
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password',message='passwords do not match!')], render_kw={'class':'form-control', 'placeholder':' '})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()], render_kw={'class':'form-control', 'placeholder':' '})
    city = SelectField('City', choices=['GLASGOW'], validators=[DataRequired()], render_kw={'class':'form-select', 'placeholder':' '})
    submit = SubmitField('Add Operator', render_kw={'class':'btn btn-primary'})
