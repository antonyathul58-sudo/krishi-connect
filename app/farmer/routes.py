import os
import secrets
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from app import db
from app.forms import CropForm
from app.models import Crop, Inquiry, CropAlert, Notification
from flask_login import current_user, login_required

farmer = Blueprint('farmer', __name__)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/uploads', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@farmer.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != 'farmer':
        flash('Access Denied: You must be a farmer to view this page.', 'danger')
        return redirect(url_for('main.home'))
    
    crops = Crop.query.filter_by(farmer_id=current_user.id).order_by(Crop.date_posted.desc()).all()
    inquiries = current_user.inquiries_received
    
    return render_template('farmer/dashboard.html', title='Farmer Dashboard', crops=crops, inquiries=inquiries)

@farmer.route("/crop/new", methods=['GET', 'POST'])
@login_required
def new_crop():
    if current_user.role != 'farmer':
        flash('Access Denied', 'danger')
        return redirect(url_for('main.home'))
        
    form = CropForm()
    if form.validate_on_submit():
        picture_file = 'default_crop.jpg'
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            
        crop = Crop(name=form.name.data, quantity=form.quantity.data, price=form.price.data,
                    location=form.location.data, description=form.description.data, 
                    image_file=picture_file, farmer=current_user)
        db.session.add(crop)
        db.session.commit()
        
        # Trigger Crop Alerts
        crop_name_lower = crop.name.lower().strip()
        alerts = CropAlert.query.filter_by(is_active=True).all()
        for alert in alerts:
            alert_name_lower = alert.crop_name.lower().strip()
            # Fuzzy match
            if alert_name_lower in crop_name_lower or crop_name_lower in alert_name_lower:
                notification = Notification(
                    message=f"Alarm! A new listing for '{crop.name}' (₹{crop.price}/kg) has just been posted by {current_user.username}.",
                    user_id=alert.buyer_id,
                    crop_id=crop.id
                )
                db.session.add(notification)
        db.session.commit()
        
        flash('Your crop listing has been created!', 'success')
        return redirect(url_for('farmer.dashboard'))
    return render_template('farmer/add_crop.html', title='List New Crop', form=form, legend='List New Crop')

@farmer.route("/crop/<int:crop_id>/delete", methods=['POST'])
@login_required
def delete_crop(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    if crop.farmer != current_user:
        flash('Access Denied', 'danger')
        return redirect(url_for('farmer.dashboard'))
    db.session.delete(crop)
    db.session.commit()
    flash('Your crop listing has been deleted!', 'success')
    return redirect(url_for('farmer.dashboard'))
