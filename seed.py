from app import create_app, db, bcrypt
from app.models import User, Crop, Inquiry, CropAlert, Notification

app = create_app()

with app.app_context():
    print("Recreating database schema...")
    db.drop_all()
    db.create_all()
    
    print("Seeding database...")
    
    # Create users
    hashed_pw = bcrypt.generate_password_hash('password123').decode('utf-8')
    
    admin = User(username='admin', email='admin@krishiconnect.com', password=hashed_pw, role='admin')
    farmer1 = User(username='ramesh_farmer', email='ramesh@example.com', password=hashed_pw, role='farmer')
    farmer2 = User(username='suresh_farmer', email='suresh@example.com', password=hashed_pw, role='farmer')
    buyer1 = User(username='kisan_traders', email='traders@example.com', password=hashed_pw, role='buyer')
    buyer2 = User(username='fresh_foods', email='fresh@example.com', password=hashed_pw, role='buyer')
    
    db.session.add_all([admin, farmer1, farmer2, buyer1, buyer2])
    db.session.commit()
    
    print("Users created.")
    
    # Create crops
    crop1 = Crop(name='Organic Wheat', quantity=500.0, price=25.0, location='Punjab, India', 
                 description='High-quality organic wheat grown without chemical fertilizers.', 
                 farmer=farmer1)
    
    crop2 = Crop(name='Basmati Rice', quantity=2000.0, price=80.0, location='Haryana, India', 
                 description='Premium long-grain Basmati rice, aged for 1 year.', 
                 farmer=farmer1)
                 
    crop3 = Crop(name='Fresh Tomatoes', quantity=100.0, price=40.0, location='Maharashtra, India', 
                 description='Farm-fresh red tomatoes, hand-picked this morning.', 
                 farmer=farmer2)

    crop4 = Crop(name='Alphonso Mangoes', quantity=50.0, price=500.0, location='Ratnagiri, Maharashtra', 
                 description='Sweet and juicy Alphonso mangoes straight from the orchard.', 
                 farmer=farmer2)
                 
    db.session.add_all([crop1, crop2, crop3, crop4])
    db.session.commit()
    
    print("Crops created.")
    
    # Create inquiries
    inq1 = Inquiry(subject='Interested in bulk buying', 
                   message='Hi Ramesh, we would like to buy 200kg of your organic wheat. Is the price negotiable?', 
                   sender=buyer1, receiver_id=farmer1.id, crop=crop1)
                   
    inq2 = Inquiry(subject='Mango availability', 
                   message='Hello Suresh, are the Alphonso mangoes ripe and ready to eat?', 
                   sender=buyer2, receiver_id=farmer2.id, crop=crop4)
                   
    db.session.add_all([inq1, inq2])
    db.session.commit()
    
    print("Inquiries created. Seeding complete!")
