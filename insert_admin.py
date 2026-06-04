from app import app
from models.models import db, Admin
from werkzeug.security import generate_password_hash

with app.app_context():

    # Check if admin already exists
    existing_admin = Admin.query.filter_by(
        username="admin"
    ).first()

    if existing_admin:
        print("Admin already exists!")

    else:
        admin = Admin(
            username="admin",
            password=generate_password_hash("admin123")
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully!")