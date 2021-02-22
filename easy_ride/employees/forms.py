from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_login import current_user
from easy_ride.models import User, BikeInfo, Repair

class MoveBikeForm(FlaskForm):
    def bike_move_check(self, field):
        bike = BikeInfo.query.filter_by(bike_number=field.data).first()
        if not bike:
            raise ValidationError('No bike found with the given number')
        else:
            if not bike.status.name == 'YES':
                  raise ValidationError('Bike not available to move' )

    bike_number = IntegerField('Bike Number', validators=[DataRequired(), bike_move_check], render_kw={'class':'form-control'})
    new_location = SelectField('Moved location', validators=[DataRequired()], choices=['HILLHEAD', 'PARTICK', 'FINNIESTON', 'GOVAN', 'LAURIESTON'], render_kw={'class':'form-select'})
    submit = SubmitField('Change Location', render_kw={'class':'btn btn-primary'})

class RepairBikeForm(FlaskForm):
    def bike_repair_check(self, field):
        if not Repair.query.filter_by(bike_number=field.data, repair_status='NO').first():
            raise ValidationError('No bike reported with the given number')

    bike_number = IntegerField('Bike Number', validators=[DataRequired(), bike_repair_check], render_kw={'class':'form-control'})
    level_of_repair = SelectField('Level of repair', validators=[DataRequired()], choices=[0, 1, 2, 3, 4, 5], render_kw={'class':'form-select'})
    comment = TextAreaField('Comment', validators=[DataRequired()], render_kw={'class':'form-control'})
    submit = SubmitField('Complete Repair', render_kw={'class':'btn btn-primary'})

class AddOperatorForm(FlaskForm):
    def check_email_reg(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('This email has already been registered.')

    def check_phone_reg(self, field):
        if User.query.filter_by(phone_number=field.data).first():
            raise ValidationError('This phone number has already been registered.')

    first_name = StringField('First Name', validators=[DataRequired()], render_kw={'class':'form-control'})
    last_name = StringField('Last Name', validators=[DataRequired()], render_kw={'class':'form-control'})
    phone_number = IntegerField('Phone Number', validators=[DataRequired(), check_phone_reg], render_kw={'class':'form-control'})
    email = StringField('Email', validators = [DataRequired(), Email(), check_email_reg], render_kw={'class':'form-control'})
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password',message='passwords do not match!')], render_kw={'class':'form-control'})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()], render_kw={'class':'form-control'})
    city = SelectField('City', choices=['GLASGOW'], validators=[DataRequired()], render_kw={'class':'form-select'})
    submit = SubmitField('Add Operator', render_kw={'class':'btn btn-primary'})
