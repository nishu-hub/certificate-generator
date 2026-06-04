from models.models import * 
from flask import Flask, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models.models import db, Event, Participant, Certificate, VerificationLog

# Auth Routes
from routes.auth import login, logout

# Participant Routes
from routes.participant_routes import (
    upload_participants,
    export_participants
)
from routes.participant_list_routes import participant_list

# Blueprints
from routes.admin_routes import admin_bp
from routes.certificate_routes import certificate_bp 
from routes.event_routes import event_bp



from utils.decorators import admin_required 

from flask_migrate import Migrate




# ==========================
# APP INITIALIZATION
# ==========================

app = Flask(__name__)

# Load configuration (single source of truth)
app.config.from_object("config.Config")

# Initialize DB
db.init_app(app) 


migrate = Migrate(app, db) 

# Register Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(certificate_bp)
app.register_blueprint(event_bp)


# ==========================
# AUTH ROUTES
# ==========================

app.add_url_rule(
    "/login",
    view_func=login,
    methods=["GET", "POST"]
)

app.add_url_rule(
    "/logout",
    view_func=logout,
    methods=["GET"]
)


# ==========================
# PARTICIPANT ROUTES
# ==========================

app.add_url_rule(
    "/upload-participants",
    view_func=upload_participants,
    methods=["GET", "POST"]
)

app.add_url_rule(
    "/participants",
    view_func=participant_list
) 

app.add_url_rule(
    "/export-participants",
    view_func=export_participants
)


# ==========================
# DASHBOARD
# ==========================

@app.route("/")
@admin_required
def home_dashboard():

    event_count = Event.query.count()
    participant_count = Participant.query.count()
    certificate_count = Certificate.query.count()
    verification_count = VerificationLog.query.count()

    recent_logs = VerificationLog.query.order_by(
        VerificationLog.scan_time.desc()
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        event_count=event_count,
        participant_count=participant_count,
        certificate_count=certificate_count,
        verification_count=verification_count,
        recent_logs=recent_logs
    )

@app.errorhandler(404)
def not_found(error):
    return render_template(
        "404.html"
    ), 404 
    
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()

    return render_template(
        "500.html"
    ), 500

# ==========================
# CREATE TABLES (DEV ONLY)
# ==========================

with app.app_context():
    db.create_all()


# ==========================
# RUN APPLICATION
# ==========================

if __name__ == "__main__":
    app.run(debug=True)