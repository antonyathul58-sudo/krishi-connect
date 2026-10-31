import os
import random
import secrets
import time
from flask import render_template, url_for, flash, redirect, request, session, Blueprint, current_app
from flask_mail import Message
from app import db, bcrypt, mail, limiter
from app.forms import (RegistrationForm, LoginForm, LoginVerifyOTPForm, BuyerRegistrationForm, 
                       OTPVerificationForm, ForgotPasswordForm, ResetPasswordForm, UpdateProfileForm)
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required

auth = Blueprint('auth', __name__)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', 'uploads', picture_fn)
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    form_picture.save(picture_path)
    return picture_fn

def send_otp_email(user_email, otp_code):
    try:
        msg = Message('Your Krishi Connect Verification Code',
                      recipients=[user_email])
        msg.body = f'''Your One-Time Password (OTP) for Krishi Connect is: {otp_code}

Please enter this code on the verification page to proceed. 
If you did not request this, please ignore this email.
'''
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

@auth.route("/register")
def register_selection():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return render_template('auth/register_selection.html', title='Choose Account Type')

@auth.route("/register/farmer", methods=['GET', 'POST'])
def register_farmer():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        otp_code = str(random.randint(100000, 999999))
        session['pending_user'] = {
            'username': form.username.data,
            'email': form.email.data,
            'phone_number': form.phone_number.data,
            'district': form.district.data,
            'state': form.state.data,
            'country': form.country.data,
            'password': hashed_password,
            'role': 'farmer'
        }
        session['otp_code'] = otp_code
        send_otp_email(form.email.data, otp_code)
        flash(f'🔐 Verification OTP sent to {form.email.data}. Please check your inbox (and spam folder).', 'info')
        return redirect(url_for('auth.verify_otp'))
    return render_template('auth/register_farmer.html', title='Register as Farmer', form=form)

@auth.route("/register/buyer", methods=['GET', 'POST'])
def register_buyer():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = BuyerRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        otp_code = str(random.randint(100000, 999999))
        session['pending_user'] = {
            'username': form.username.data,
            'email': form.email.data,
            'phone_number': form.phone_number.data,
            'district': form.district.data,
            'state': form.state.data,
            'country': form.country.data,
            'password': hashed_password,
            'role': form.buyer_type.data
        }
        session['otp_code'] = otp_code
        send_otp_email(form.email.data, otp_code)
        flash(f'🔐 Verification OTP sent to {form.email.data}. Please check your inbox.', 'info')
        return redirect(url_for('auth.verify_otp'))
    return render_template('auth/register_buyer.html', title='Register as Buyer', form=form)

@auth.route("/verify-otp", methods=['GET', 'POST'])
def verify_otp():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    pending_user = session.get('pending_user')
    stored_otp = session.get('otp_code')
    
    if not pending_user or not stored_otp:
        flash('No pending registration session found. Please register again.', 'warning')
        return redirect(url_for('auth.register_selection'))

    form = OTPVerificationForm()
    if form.validate_on_submit():
        if form.otp.data.strip() == stored_otp:
            user = User(
                username=pending_user['username'],
                email=pending_user['email'],
                phone_number=pending_user['phone_number'],
                district=pending_user.get('district', 'Ernakulam'),
                state=pending_user.get('state', 'Kerala'),
                country=pending_user.get('country', 'India'),
                password=pending_user['password'],
                role=pending_user['role'],
                is_verified=True
            )
            db.session.add(user)
            db.session.commit()
            
            session.pop('pending_user', None)
            session.pop('otp_code', None)
            
            flash('✅ Registration & OTP verification successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('❌ Incorrect OTP code. Please check and try again.', 'danger')

    return render_template('auth/verify_otp.html', title='OTP Verification', form=form, pending_user=pending_user, current_otp=stored_otp)

@auth.route("/forgot-password", methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        identifier = form.email_or_phone.data.strip()
        user = User.query.filter((User.email == identifier) | (User.phone_number == identifier)).first()
        if user:
            reset_otp = str(random.randint(100000, 999999))
            session['reset_user_id'] = user.id
            session['reset_otp_code'] = reset_otp
            send_otp_email(user.email, reset_otp)
            flash(f'🔑 Password reset OTP sent to {user.email}. Please check your inbox.', 'info')
            return redirect(url_for('auth.reset_password'))
        else:
            flash('No account found with that email address or phone number.', 'danger')
            
    return render_template('auth/forgot_password.html', title='Forgot Password', form=form)

@auth.route("/reset-password", methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    reset_user_id = session.get('reset_user_id')
    stored_reset_otp = session.get('reset_otp_code')
    
    if not reset_user_id or not stored_reset_otp:
        flash('Password reset session expired or invalid. Please try again.', 'warning')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.get_or_404(reset_user_id)
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        if form.otp.data.strip() == stored_reset_otp:
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            
            session.pop('reset_user_id', None)
            session.pop('reset_otp_code', None)
            
            flash('✅ Password updated successfully! Please log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('❌ Invalid OTP code. Please enter the correct verification code.', 'danger')

    return render_template('auth/reset_password.html', title='Reset Password', form=form, user=user, current_otp=stored_reset_otp)

@auth.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm(obj=current_user)
    if form.validate_on_submit():
        existing_username = User.query.filter(User.username == form.username.data, User.id != current_user.id).first()
        if existing_username:
            flash('That username is already taken. Please choose another.', 'danger')
            return render_template('auth/profile.html', title='Edit Profile', form=form)
            
        existing_email = User.query.filter(User.email == form.email.data, User.id != current_user.id).first()
        if existing_email:
            flash('That email address is already registered to another account.', 'danger')
            return render_template('auth/profile.html', title='Edit Profile', form=form)

        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone_number = form.phone_number.data
        current_user.district = form.district.data
        current_user.state = form.state.data
        current_user.country = form.country.data
        
        if form.new_password.data:
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            
        db.session.commit()
        flash('✨ Your profile details and location have been updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone_number.data = current_user.phone_number
        form.district.data = current_user.district or 'Ernakulam'
        form.state.data = current_user.state or 'Kerala'
        form.country.data = current_user.country or 'India'

    image_file = url_for('static', filename='uploads/' + (current_user.image_file or 'default.jpg'))
    return render_template('auth/profile.html', title='My Profile', form=form, image_file=image_file)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.email_or_phone.data.strip()
        user = User.query.filter((User.email == identifier) | (User.phone_number == identifier)).first()
        
        if user:
            otp_code = str(random.randint(100000, 999999))
            session['login_user_id'] = user.id
            session['login_otp_code'] = otp_code
            session['login_otp_timestamp'] = time.time()
            session['login_remember'] = form.remember.data
            
            send_otp_email(user.email, otp_code)
            flash(f'🔐 Verification OTP sent to {user.email}. Please check your inbox.', 'info')
            return redirect(url_for('auth.login_verify'))
        else:
            flash('No account found with that email or phone number.', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@auth.route("/login/verify", methods=['GET', 'POST'])
def login_verify():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    login_user_id = session.get('login_user_id')
    stored_otp = session.get('login_otp_code')
    otp_timestamp = session.get('login_otp_timestamp')
    
    if not login_user_id or not stored_otp or not otp_timestamp:
        flash('Login session expired or invalid. Please try again.', 'warning')
        return redirect(url_for('auth.login'))
        
    # Check 5 minutes expiration (300 seconds)
    if time.time() - otp_timestamp > 300:
        session.pop('login_user_id', None)
        session.pop('login_otp_code', None)
        session.pop('login_otp_timestamp', None)
        flash('OTP has expired (valid for 5 minutes). Please login again to request a new code.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(login_user_id)
    form = LoginVerifyOTPForm()
    
    if form.validate_on_submit():
        if form.otp.data.strip() == stored_otp:
            login_user(user, remember=session.get('login_remember', False))
            session.pop('login_user_id', None)
            session.pop('login_otp_code', None)
            session.pop('login_otp_timestamp', None)
            session.pop('login_remember', None)
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.role == 'farmer':
                return redirect(url_for('farmer.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('buyer.dashboard'))
        else:
            flash('❌ Invalid OTP code. Please enter the correct verification code.', 'danger')
            
    return render_template('auth/verify_login_otp.html', title='Verify Login', form=form, user=user)

@auth.route("/login/resend")
@limiter.limit("3 per minute", error_message="Too many requests. Please wait before asking for another OTP.")
def login_resend():
    login_user_id = session.get('login_user_id')
    if not login_user_id:
        flash('No active login session found.', 'warning')
        return redirect(url_for('auth.login'))
        
    user = User.query.get_or_404(login_user_id)
    otp_code = str(random.randint(100000, 999999))
    session['login_otp_code'] = otp_code
    session['login_otp_timestamp'] = time.time()
    
    send_otp_email(user.email, otp_code)
    flash('A new OTP has been sent to your email.', 'success')
    return redirect(url_for('auth.login_verify'))

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))
