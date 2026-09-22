from flask import render_template, url_for, flash, redirect, request, Blueprint
from app import db
from app.models import Crop, Inquiry, User, CropAlert, Notification
from app.forms import InquiryForm, CropAlertForm
from flask_login import current_user, login_required

buyer = Blueprint('buyer', __name__)

@buyer.route("/dashboard")
@login_required
def dashboard():
    if current_user.role not in ['buyer', 'shop_owner', 'individual']:
        flash('Access Denied', 'danger')
        return redirect(url_for('main.home'))
    
    # Buyer sees their sent inquiries
    inquiries = current_user.inquiries_sent
    return render_template('buyer/dashboard.html', title='Buyer Dashboard', inquiries=inquiries)

@buyer.route("/browse")
@login_required
def browse():
    # Marketplace: view all crops
    page = request.args.get('page', 1, type=int)
    crops = Crop.query.order_by(Crop.date_posted.desc()).paginate(page=page, per_page=12)
    return render_template('buyer/browse.html', title='Marketplace', crops=crops)

@buyer.route("/crop/<int:crop_id>", methods=['GET', 'POST'])
@login_required
def crop_detail(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    form = InquiryForm()
    
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Please log in to send an inquiry.', 'info')
            return redirect(url_for('auth.login', next=request.url))
            
        inquiry = Inquiry(subject=form.subject.data, message=form.message.data,
                          sender=current_user, receiver_id=crop.farmer_id, crop_id=crop.id)
        db.session.add(inquiry)
        db.session.commit()
        flash('Your inquiry has been sent to the farmer!', 'success')
        return redirect(url_for('buyer.crop_detail', crop_id=crop.id))
        
    return render_template('buyer/crop_detail.html', title=crop.name, crop=crop, form=form)

@buyer.route("/alerts", methods=['GET', 'POST'])
@login_required
def alerts():
    if current_user.role not in ['buyer', 'shop_owner', 'individual']:
        flash('Access Denied', 'danger')
        return redirect(url_for('main.home'))
        
    form = CropAlertForm()
    if form.validate_on_submit():
        alert = CropAlert(crop_name=form.crop_name.data.lower().strip(), buyer=current_user)
        db.session.add(alert)
        db.session.commit()
        flash(f'Alert set for {form.crop_name.data}!', 'success')
        return redirect(url_for('buyer.alerts'))
        
    user_alerts = CropAlert.query.filter_by(buyer_id=current_user.id).order_by(CropAlert.date_created.desc()).all()
    return render_template('buyer/alerts.html', title='My Crop Alerts', form=form, alerts=user_alerts)

@buyer.route("/alerts/<int:alert_id>/delete", methods=['POST'])
@login_required
def delete_alert(alert_id):
    alert = CropAlert.query.get_or_404(alert_id)
    if alert.buyer_id != current_user.id:
        flash('Access Denied', 'danger')
        return redirect(url_for('buyer.alerts'))
    db.session.delete(alert)
    db.session.commit()
    flash('Alert deleted.', 'success')
    return redirect(url_for('buyer.alerts'))

@buyer.route("/notifications")
@login_required
def notifications():
    user_notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.date_created.desc()).all()
    # Mark as read
    for n in user_notifs:
        if not n.is_read:
            n.is_read = True
    db.session.commit()
    
    return render_template('buyer/notifications.html', title='My Notifications', notifications=user_notifs)
