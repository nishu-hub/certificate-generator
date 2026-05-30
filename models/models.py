from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


# ==========================
# ADMIN TABLE
# ==========================

class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )


# ==========================
# PARTICIPANT TABLE
# ==========================

class Participant(db.Model):
    __tablename__ = "participants"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    college = db.Column(
        db.String(100)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    certificate = db.relationship(
        "Certificate",
        backref="participant",
        uselist=False,
        cascade="all, delete-orphan"
    )


# ==========================
# EVENT TABLE
# ==========================

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    date = db.Column(
        db.String(50),      # change to db.Date later if desired
        nullable=False
    )

    organizer = db.Column(
        db.String(150),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class VerificationLog(db.Model): 
    __tablename__ = "verification_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    certificate_id = db.Column(
        db.String(36),
        db.ForeignKey("certificates.id"),
        nullable=False
    )

    verified_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# ==========================
# CERTIFICATE TABLE
# ==========================

class Certificate(db.Model):
    __tablename__ = "certificates"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    participant_id = db.Column(
        db.Integer,
        db.ForeignKey("participants.id"),
        unique=True,
        nullable=False
    )

    issued_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    qr_path = db.Column(
        db.String(255),
        nullable=True
    ) 
    
    logs = db.relationship(
    "VerificationLog",
    backref="certificate",
    lazy=True,
    cascade="all, delete-orphan"
)

    def __repr__(self):
        return f"<Certificate {self.id}>"