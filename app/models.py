from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='buyer') # farmer, buyer, admin
    
    crops = db.relationship('Crop', backref='farmer', lazy=True)
    inquiries_sent = db.relationship('Inquiry', foreign_keys='Inquiry.sender_id', backref='sender', lazy=True)
    inquiries_received = db.relationship('Inquiry', foreign_keys='Inquiry.receiver_id', backref='receiver', lazy=True)
    
    crop_alerts = db.relationship('CropAlert', backref='buyer', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False) # e.g., in kg
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_file = db.Column(db.String(100), nullable=False, default='default_crop.jpg')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    farmer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    inquiries = db.relationship('Inquiry', backref='crop', lazy=True)

    def __repr__(self):
        return f"Crop('{self.name}', '{self.price}', '{self.location}')"

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=True)

    def __repr__(self):
        return f"Inquiry('{self.subject}', '{self.date_sent}')"

class CropAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"CropAlert('{self.crop_name}', '{self.date_created}')"

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=True)

    def __repr__(self):
        return f"Notification('{self.message}', '{self.date_created}')"
