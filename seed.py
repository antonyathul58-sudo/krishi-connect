from app import create_app, db, bcrypt
from app.models import User, Crop, Inquiry, CropAlert, Notification, Transaction

app = create_app()

with app.app_context():
    print("Recreating database schema...")
    db.drop_all()
    db.create_all()
    
    print("Seeding database...")
    
    # Create users
    hashed_pw = bcrypt.generate_password_hash('password123').decode('utf-8')
    
    admin = User(username='admin', email='admin@krishiconnect.com', phone_number='+919876543210', password=hashed_pw, role='admin', is_verified=True)
    farmer1 = User(username='ramesh_farmer', email='ramesh@example.com', phone_number='+919876543211', password=hashed_pw, role='farmer', is_verified=True)
    farmer2 = User(username='suresh_farmer', email='suresh@example.com', phone_number='+919876543212', password=hashed_pw, role='farmer', is_verified=True)
    buyer1 = User(username='kisan_traders', email='traders@example.com', phone_number='+919876543213', password=hashed_pw, role='buyer', is_verified=True)
    buyer2 = User(username='fresh_foods', email='fresh@example.com', phone_number='+919876543214', password=hashed_pw, role='buyer', is_verified=True)
    
    db.session.add_all([admin, farmer1, farmer2, buyer1, buyer2])
    db.session.commit()
    
    print("Users created.")
    
    # Create crops with categories
    crop1 = Crop(name='Organic Wheat', category='Grains', quantity=500.0, price=25.0, location='Punjab, India', 
                 description='High-quality organic wheat grown without chemical fertilizers.', 
                 image_file='organic_wheat.png', farmer=farmer1)
    
    crop2 = Crop(name='Basmati Rice', category='Grains', quantity=2000.0, price=80.0, location='Haryana, India', 
                 description='Premium long-grain Basmati rice, aged for 1 year.', 
                 image_file='basmati_rice.png', farmer=farmer1)
                 
    crop3 = Crop(name='Fresh Tomatoes', category='Vegetables', quantity=100.0, price=40.0, location='Maharashtra, India', 
                 description='Farm-fresh red tomatoes, hand-picked this morning.', 
                 image_file='fresh_tomatoes.png', farmer=farmer2)

    crop4 = Crop(name='Alphonso Mangoes', category='Fruits', quantity=50.0, price=500.0, location='Ratnagiri, Maharashtra', 
                 description='Sweet and juicy Alphonso mangoes straight from the orchard.', 
                 image_file='alphonso_mangoes.png', farmer=farmer2)
                 
    db.session.add_all([crop1, crop2, crop3, crop4])
    db.session.commit()
    
    print("Crops created.")
    
    # Create inquiries (Chats)
    inq1 = Inquiry(subject='Interested in bulk buying', 
                   message='Hi Ramesh, we would like to buy 200kg of your organic wheat. Is the price negotiable?', 
                   sender=buyer1, receiver=farmer1, crop=crop1)
                   
    inq2 = Inquiry(subject='Mango availability', 
                   message='Hello Suresh, are the Alphonso mangoes ripe and ready to eat?', 
                   sender=buyer2, receiver=farmer2, crop=crop4)

    inq3 = Inquiry(subject='Order confirmation', 
                   message='Thanks for sending the invoice for 100kg Basmati Rice.', 
                   sender=buyer1, receiver=farmer1, crop=crop2)
                   
    db.session.add_all([inq1, inq2, inq3])
    db.session.commit()
    
    print("Inquiries created.")

    # Create transactions
    tx1 = Transaction(quantity=100.0, unit_price=25.0, total_price=2500.0, status='Completed',
                      buyer=buyer1, farmer=farmer1, crop=crop1)
    tx2 = Transaction(quantity=50.0, unit_price=80.0, total_price=4000.0, status='Completed',
                      buyer=buyer1, farmer=farmer1, crop=crop2)
    tx3 = Transaction(quantity=20.0, unit_price=500.0, total_price=10000.0, status='Pending',
                      buyer=buyer2, farmer=farmer2, crop=crop4)
    tx4 = Transaction(quantity=30.0, unit_price=40.0, total_price=1200.0, status='Completed',
                      buyer=buyer2, farmer=farmer2, crop=crop3)

    db.session.add_all([tx1, tx2, tx3, tx4])
    db.session.commit()

    print("Transactions created. Seeding complete!")
