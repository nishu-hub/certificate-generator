from app import app
from models.models import db, Admin
from werkzeug.security import generate_password_hash

with app.app_context():
    
    hashed_password = generate_password_hash("admin123")

    admin = Admin(
        username="admin",
        password=hashed_password
    ) 
    admins = Admin.query.all()

    db.session.add(admin)

    db.session.commit()

    print("Admin Added Successfully")