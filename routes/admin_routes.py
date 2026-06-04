from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    session
)

from functools import wraps
import os

from models.models import (
    db,
    Participant,
    Certificate,
    Event
)  

from models.models import (
    Event,
    Participant,
    Certificate,
    VerificationLog
)

# ==========================
# BLUEPRINT
# ==========================

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

# ==========================
# LOGIN REQUIRED DECORATOR
# ==========================

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "admin_id" not in session:
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper


# ==========================
# ADMIN DASHBOARD
# ==========================

@admin_bp.route("/dashboard")
@login_required
def dashboard():

    event_count = Event.query.count()

    participant_count = Participant.query.count()

    certificate_count = Certificate.query.count()

    verification_count = VerificationLog.query.count()

    recent_logs = VerificationLog.query.order_by(
        VerificationLog.scan_time.desc()
).limit(5).all()


    return render_template(
        "admin_dashboard.html",
        event_count=event_count,
        participant_count=participant_count,
        certificate_count=certificate_count,
        verification_count=verification_count,
        recent_logs=recent_logs
    )

# ========================== 
# EVENTS LIST
# ==========================
@admin_bp.route("/events")
@login_required
def events():

    events = Event.query.all()

    return render_template(
        "events.html",
        events=events
    )
    
    

# ==========================
# PARTICIPANT LIST
# ==========================

@admin_bp.route("/participants")
@login_required
def participants():

    participants = Participant.query.all()

    return render_template(
        "participants.html",
        participants=participants
    )


# ==========================
# SEARCH PARTICIPANTS
# ==========================

@admin_bp.route("/search")
@login_required
def search():

    keyword = request.args.get(
        "q",
        ""
    ).strip()

    results = Participant.query.filter(
        Participant.name.ilike(
            f"%{keyword}%"
        )
    ).all()

    return render_template(
        "participants.html",
        participants=results
    )


# ==========================
# CERTIFICATE LIST
# ==========================

@admin_bp.route("/certificates")
@login_required
def certificates():

    certificates = Certificate.query.all()

    return render_template(
        "certificates.html",
        certificates=certificates
    )


# ==========================
# CERTIFICATE DETAIL
# ==========================

@admin_bp.route(
    "/certificate/<certificate_id>"
)
@login_required
def certificate_detail(
    certificate_id
):

    certificate = (
        Certificate.query
        .get_or_404(certificate_id)
    )

    return render_template(
        "certificate_detail.html",
        certificate=certificate
    )


# ==========================
# DELETE CERTIFICATE
# ==========================

@admin_bp.route(
    "/delete-certificate/<certificate_id>",
    methods=["POST"]
)
@login_required
def delete_certificate(
    certificate_id
):

    certificate = (
        Certificate.query
        .get_or_404(certificate_id)
    )

    db.session.delete(certificate)
    db.session.commit()

    flash(
        "Certificate deleted successfully",
        "success"
    )

    return redirect(
        url_for(
            "admin.certificates"
        )
    )


# ==========================
# DOWNLOAD CERTIFICATE PDF
# ==========================

@admin_bp.route(
    "/download/<certificate_id>"
)
@login_required
def download_certificate(
    certificate_id
):

    certificate = (
        Certificate.query
        .get_or_404(certificate_id)
    )

    pdf_path = os.path.join(
        "certificates",
        f"{certificate.id}.pdf"
    )

    if not os.path.exists(pdf_path):

        flash(
            "PDF file not found",
            "danger"
        )

        return redirect(
            url_for(
                "admin.certificates"
            )
        )

    return send_file(
        pdf_path,
        as_attachment=True
    )