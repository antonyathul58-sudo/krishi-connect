from app import create_app, db
import os

app = create_app()

with app.app_context():
    db.create_all()
    # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
