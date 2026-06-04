from werkzeug.security import generate_password_hash

from app import app
from models.models import db, Admin


with app.app_context():

    username = "admin"

    password = "admin123"

    existing_admin = Admin.query.filter_by(
        username=username
    ).first()

    if existing_admin:

        print("Admin already exists.")

    else:

        admin = Admin(
            username=username,
            password=generate_password_hash(password)
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully.")
        print("Username:", username)
        print("Password:", password)