from flask import render_template, url_for, flash, redirect, Blueprint
from app import db
from app.models import User, Crop, Inquiry
from flask_login import current_user, login_required

admin = Blueprint('admin', __name__)

@admin.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access Denied: Admin only.', 'danger')
        return redirect(url_for('main.home'))
        
    users_count = User.query.count()
    crops_count = Crop.query.count()
    inquiries_count = Inquiry.query.count()
    users = User.query.all()
    
    return render_template('admin/dashboard.html', title='Admin Dashboard', 
                           users_count=users_count, crops_count=crops_count, 
                           inquiries_count=inquiries_count, users=users)

@admin.route("/user/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))
        
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot delete yourself!', 'warning')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
        
    return redirect(url_for('admin.dashboard'))

@admin.route("/crops")
@login_required
def manage_crops():
    if current_user.role != 'admin':
        flash('Access Denied: Admin only.', 'danger')
        return redirect(url_for('main.home'))
    
    crops = Crop.query.all()
    return render_template('admin/crops.html', title='Manage Crops', crops=crops)

@admin.route("/crop/<int:crop_id>/delete", methods=['POST'])
@login_required
def delete_crop(crop_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))
        
    crop = Crop.query.get_or_404(crop_id)
    db.session.delete(crop)
    db.session.commit()
    flash('Crop deleted successfully.', 'success')
    return redirect(url_for('admin.manage_crops'))

@admin.route("/inquiries")
@login_required
def manage_inquiries():
    if current_user.role != 'admin':
        flash('Access Denied: Admin only.', 'danger')
        return redirect(url_for('main.home'))
    
    inquiries = Inquiry.query.all()
    return render_template('admin/inquiries.html', title='Manage Inquiries', inquiries=inquiries)

@admin.route("/inquiry/<int:inquiry_id>/delete", methods=['POST'])
@login_required
def delete_inquiry(inquiry_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))
        
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    db.session.delete(inquiry)
    db.session.commit()
    flash('Inquiry deleted successfully.', 'success')
    return redirect(url_for('admin.manage_inquiries'))
