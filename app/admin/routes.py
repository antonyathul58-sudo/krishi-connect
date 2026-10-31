from flask import render_template, url_for, flash, redirect, request, Blueprint
from app import db
from app.models import User, Crop, Inquiry, Transaction
from flask_login import current_user, login_required

admin = Blueprint('admin', __name__)

@admin.route("/")
@admin.route("/index")
@admin.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access Denied: Admin only.', 'danger')
        return redirect(url_for('main.home'))
        
    users_count = User.query.count()
    crops_count = Crop.query.count()
    inquiries_count = Inquiry.query.count()
    transactions_count = Transaction.query.count()
    
    q = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '').strip()

    user_query = User.query
    if role_filter and role_filter != 'all':
        user_query = user_query.filter(User.role == role_filter)
    if q:
        user_query = user_query.filter(
            (User.username.ilike(f"%{q}%")) | (User.email.ilike(f"%{q}%"))
        )
    users = user_query.all()
    
    return render_template('admin/index.html', title='Admin Dashboard', 
                           users_count=users_count, crops_count=crops_count, 
                           inquiries_count=inquiries_count, transactions_count=transactions_count,
                           users=users, search_query=q, selected_role=role_filter)

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
    
    q = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()

    crop_query = Crop.query
    if category_filter and category_filter != 'all':
        crop_query = crop_query.filter(Crop.category == category_filter)
    if q:
        crop_query = crop_query.join(User, Crop.farmer_id == User.id).filter(
            (Crop.name.ilike(f"%{q}%")) | 
            (Crop.location.ilike(f"%{q}%")) |
            (User.username.ilike(f"%{q}%"))
        )
    crops = crop_query.order_by(Crop.date_posted.desc()).all()

    categories = ['Grains', 'Pulses', 'Vegetables', 'Fruits', 'Spices', 'Oilseeds', 'Other']
    return render_template('admin/crops.html', title='Manage Crops', crops=crops, 
                           categories=categories, search_query=q, selected_category=category_filter)

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
    
    q = request.args.get('q', '').strip()
    inquiry_query = Inquiry.query

    if q:
        Sender = db.aliased(User, name='sender_alias')
        Receiver = db.aliased(User, name='receiver_alias')
        inquiry_query = inquiry_query.join(Sender, Inquiry.sender_id == Sender.id)\
                                     .join(Receiver, Inquiry.receiver_id == Receiver.id)\
                                     .outerjoin(Crop, Inquiry.crop_id == Crop.id)\
                                     .filter(
                                         (Inquiry.subject.ilike(f"%{q}%")) |
                                         (Inquiry.message.ilike(f"%{q}%")) |
                                         (Sender.username.ilike(f"%{q}%")) |
                                         (Receiver.username.ilike(f"%{q}%")) |
                                         (Crop.name.ilike(f"%{q}%"))
                                     )

    inquiries = inquiry_query.order_by(Inquiry.date_sent.desc()).all()
    return render_template('admin/inquiries.html', title='Monitor Chats & Inquiries', inquiries=inquiries, search_query=q)

@admin.route("/inquiry/<int:inquiry_id>/delete", methods=['POST'])
@login_required
def delete_inquiry(inquiry_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))
        
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    db.session.delete(inquiry)
    db.session.commit()
    flash('Inquiry message deleted successfully.', 'success')
    return redirect(url_for('admin.manage_inquiries'))

@admin.route("/transactions")
@login_required
def manage_transactions():
    if current_user.role != 'admin':
        flash('Access Denied: Admin only.', 'danger')
        return redirect(url_for('main.home'))

    q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()

    tx_query = Transaction.query

    if status_filter and status_filter != 'all':
        tx_query = tx_query.filter(Transaction.status == status_filter)

    if q:
        Buyer = db.aliased(User, name='buyer_alias')
        Farmer = db.aliased(User, name='farmer_alias')
        tx_query = tx_query.join(Buyer, Transaction.buyer_id == Buyer.id)\
                           .join(Farmer, Transaction.farmer_id == Farmer.id)\
                           .outerjoin(Crop, Transaction.crop_id == Crop.id)\
                           .filter(
                               (Buyer.username.ilike(f"%{q}%")) |
                               (Farmer.username.ilike(f"%{q}%")) |
                               (Crop.name.ilike(f"%{q}%"))
                           )

    transactions = tx_query.order_by(Transaction.date_created.desc()).all()
    total_traded_value = sum(tx.total_price for tx in transactions if tx.status == 'Completed')

    return render_template('admin/transactions.html', title='Monitor Transactions', 
                           transactions=transactions, search_query=q, selected_status=status_filter,
                           total_traded_value=total_traded_value)

@admin.route("/transaction/<int:tx_id>/delete", methods=['POST'])
@login_required
def delete_transaction(tx_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))

    tx = Transaction.query.get_or_404(tx_id)
    db.session.delete(tx)
    db.session.commit()
    flash('Transaction record removed by admin.', 'success')
    return redirect(url_for('admin.manage_transactions'))
