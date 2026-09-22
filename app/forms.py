from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class BuyerRegistrationForm(RegistrationForm):
    buyer_type = SelectField('I am a', choices=[('shop_owner', 'Shop Owner / Business'), ('individual', 'Individual Consumer')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CropForm(FlaskForm):
    name = StringField('Crop Name', validators=[DataRequired(), Length(min=2, max=100)])
    quantity = FloatField('Quantity (e.g., kg/tons)', validators=[DataRequired()])
    price = FloatField('Price per unit', validators=[DataRequired()])
    location = StringField('Location/Farm Address', validators=[DataRequired(), Length(min=2, max=120)])
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
