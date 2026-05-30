from flask import Flask, render_template, session, redirect, url_for

from models.models import db

# Auth Routes
from routes.auth import login, logout

# Participant Routes
from routes.participant_routes import upload_participants
from routes.participant_list_routes import participant_list

# Blueprints
from routes.admin_routes import admin_bp
from routes.certificate_routes import certificate_bp


app = Flask(__name__) 

# Configure Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/certificate.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Load Configuration
app.config.from_object("config.Config")

# Initialize Database
db.init_app(app)

# Register Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(certificate_bp)

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

# ==========================
# DASHBOARD
# ==========================

@app.route("/")
def home_dashboard():

    if "admin_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")

# ==========================
# CREATE TABLES
# ==========================

with app.app_context():
    db.create_all()

# ==========================
# RUN APPLICATION
# ==========================

if __name__ == "__main__":
    app.run(debug=True)