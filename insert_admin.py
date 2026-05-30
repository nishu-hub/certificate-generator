from app import app

from models.models import db, Admin

from werkzeug.security import generate_password_hash


with app.app_context():

    # Hash the password
    hashed_password = generate_password_hash("admin123")

    # Create admin object
    admin = Admin(
        username="admin",
        password=hashed_password
    )

    # Add to database
    db.session.add(admin)

    # Save changes
    db.session.commit()

    print("Admin Added Successfully")