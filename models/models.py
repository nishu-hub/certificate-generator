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
    
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id"), 
        nullable=True)

    certificate = db.relationship(
        "Certificate",
        backref="participant",
        uselist=False,
        cascade="all, delete-orphan"
    ) 
    
    verification_logs = db.relationship(
    "VerificationLog",
    backref="participant",
    lazy=True,
    cascade="all, delete-orphan"
)
    

# ==========================
# EVENT TABLE
# ==========================

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    date = db.Column(db.Date, nullable=True)

    created_at = db.Column(db.DateTime, default=db.func.now())

# ==========================
# VERIFICATION LOG TABLE
# ==========================

class VerificationLog(db.Model):
    __tablename__ = "verification_logs"

    id = db.Column(db.Integer, primary_key=True)

    certificate_id = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    participant_id = db.Column(
        db.Integer,
        db.ForeignKey("participants.id"),
        nullable=True,
        index=True
    )

    status = db.Column(
        db.Enum("valid", "invalid", name="verification_status"),
        nullable=False
    )

    scan_time = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    ip_address = db.Column(
        db.String(100),
        nullable=True
    )

    device_info = db.Column(
        db.String(500),
        nullable=True
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
    
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id"),
        nullable=True)

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
    
    
    
    def __repr__(self):
        return f"<Certificate {self.id}>"