from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from app.models import User

DISTRICT_CHOICES = [
    ('Alappuzha', 'Alappuzha'),
    ('Ernakulam', 'Ernakulam'),
    ('Idukki', 'Idukki'),
    ('Kannur', 'Kannur'),
    ('Kasaragod', 'Kasaragod'),
    ('Kollam', 'Kollam'),
    ('Kottayam', 'Kottayam'),
    ('Kozhikode', 'Kozhikode'),
    ('Malappuram', 'Malappuram'),
    ('Palakkad', 'Palakkad'),
    ('Pathanamthitta', 'Pathanamthitta'),
    ('Thiruvananthapuram', 'Thiruvananthapuram'),
    ('Thrissur', 'Thrissur'),
    ('Wayanad', 'Wayanad'),
    ('Other', 'Other Region')
]

STATE_CHOICES = [
    ('Kerala', 'Kerala'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Karnataka', 'Karnataka'),
    ('Maharashtra', 'Maharashtra'),
    ('Punjab', 'Punjab'),
    ('Haryana', 'Haryana'),
    ('Other', 'Other State')
]

COUNTRY_CHOICES = [
    ('India', 'India'),
    ('Other', 'Other Country')
]

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(), 
        Regexp(r'^\d{10}$', message="Contact number must be exactly 10 digits without letters or special characters.")
    ])
    district = SelectField('District', choices=DISTRICT_CHOICES, default='Ernakulam', validators=[DataRequired()])
    state = SelectField('State', choices=STATE_CHOICES, default='Kerala', validators=[DataRequired()])
    country = SelectField('Nation / Country', choices=COUNTRY_CHOICES, default='India', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', 
               message="Password must be at least 8 characters long and include a letter, a number, and a special character.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Continue to OTP Verification')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please login or use a different email.')

    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user:
            raise ValidationError('That phone number is already registered.')

class BuyerRegistrationForm(RegistrationForm):
    buyer_type = SelectField('I am a', choices=[('shop_owner', 'Shop Owner / Business'), ('individual', 'Individual Consumer')], validators=[DataRequired()])
    submit = SubmitField('Continue to OTP Verification')

class LoginForm(FlaskForm):
    email_or_phone = StringField('Email Address or Phone Number', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Send OTP')

class LoginVerifyOTPForm(FlaskForm):
    otp = StringField('6-Digit OTP Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify & Login')

class OTPVerificationForm(FlaskForm):
    otp = StringField('6-Digit Verification Code (OTP)', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify & Complete Registration')

class ForgotPasswordForm(FlaskForm):
    email_or_phone = StringField('Email Address or Phone Number', validators=[DataRequired()])
    submit = SubmitField('Send OTP Code')

class ResetPasswordForm(FlaskForm):
    otp = StringField('6-Digit OTP Code', validators=[DataRequired(), Length(min=6, max=6)])
    new_password = PasswordField('New Password', validators=[
        DataRequired(), 
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', 
               message="Password must be at least 8 characters long and include a letter, a number, and a special character.")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Reset Password')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(), 
        Regexp(r'^\d{10}$', message="Contact number must be exactly 10 digits without letters or special characters.")
    ])
    district = SelectField('District', choices=DISTRICT_CHOICES, default='Ernakulam', validators=[DataRequired()])
    state = SelectField('State', choices=STATE_CHOICES, default='Kerala', validators=[DataRequired()])
    country = SelectField('Nation / Country', choices=COUNTRY_CHOICES, default='India', validators=[DataRequired()])
    picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    new_password = PasswordField('New Password (leave blank to keep current)', validators=[
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', 
               message="Password must be at least 8 characters long and include a letter, a number, and a special character.")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
    submit = SubmitField('Save Profile Changes')

class CropForm(FlaskForm):
    name = StringField('Crop Name', validators=[DataRequired(), Length(min=2, max=100)])
    category = SelectField('Category', choices=[
        ('Grains', 'Grains'),
        ('Pulses', 'Pulses'),
        ('Vegetables', 'Vegetables'),
        ('Fruits', 'Fruits'),
        ('Spices', 'Spices'),
        ('Oilseeds', 'Oilseeds'),
        ('Other', 'Other')
    ], default='Grains', validators=[DataRequired()])
    quantity = FloatField('Quantity (e.g., kg/tons)', validators=[DataRequired()])
    price = FloatField('Price per unit', validators=[DataRequired()])
    district = SelectField('District', choices=DISTRICT_CHOICES, default='Ernakulam', validators=[DataRequired()])
    state = SelectField('State', choices=STATE_CHOICES, default='Kerala', validators=[DataRequired()])
    location = StringField('Specific Farm Address / Village', validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField('Description (Optional)')
    picture = FileField('Crop Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('List Crop')

class InquiryForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(min=2, max=100)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Inquiry')

class CropAlertForm(FlaskForm):
    crop_name = StringField('Crop Name (e.g., Tomato, Wheat)', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Set Alert')
