from flask import render_template, request, Blueprint
from app.models import Crop
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    if current_user.is_authenticated:
        crops = Crop.query.order_by(Crop.date_posted.desc()).limit(6).all()
        return render_template('index.html', crops=crops)
    return render_template('landing.html', title='Welcome')

@main.route("/about")
def about():
    return render_template('about.html', title='About Us')
