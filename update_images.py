from app import create_app, db
from app.models import Crop

app = create_app()

with app.app_context():
    c1 = Crop.query.filter_by(name='Organic Wheat').first()
    if c1: c1.image_file = 'organic_wheat.png'
    
    c2 = Crop.query.filter_by(name='Basmati Rice').first()
    if c2: c2.image_file = 'basmati_rice.png'
    
    c3 = Crop.query.filter_by(name='Fresh Tomatoes').first()
    if c3: c3.image_file = 'fresh_tomatoes.png'
    
    c4 = Crop.query.filter_by(name='Alphonso Mangoes').first()
    if c4: c4.image_file = 'alphonso_mangoes.png'
    
    db.session.commit()
    print("Crop images updated successfully.")
