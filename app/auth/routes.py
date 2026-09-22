from flask import render_template, url_for, flash, redirect, request, Blueprint
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, BuyerRegistrationForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required

auth = Blueprint('auth', __name__)

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
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role='farmer')
        db.session.add(user)
        db.session.commit()
        flash('Farmer account created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register_farmer.html', title='Register as Farmer', form=form)

@auth.route("/register/buyer", methods=['GET', 'POST'])
def register_buyer():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = BuyerRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.buyer_type.data)
        db.session.add(user)
        db.session.commit()
        flash('Buyer account created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register_buyer.html', title='Register as Buyer', form=form)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            # Redirect to specific dashboard based on role
            if user.role == 'farmer':
                return redirect(url_for('farmer.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('buyer.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))
