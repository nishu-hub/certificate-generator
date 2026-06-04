import csv
from io import TextIOWrapper 

import zipfile
from io import BytesIO

from flask import (
    Blueprint,
    Response,
    render_template,
    redirect,
    request,
    url_for,
    flash
)

from models.models import (
    Event,
    VerificationLog,
    db,
    Certificate,
    Participant
)

import uuid
import os
import qrcode

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from utils.decorators import admin_required


certificate_bp = Blueprint(
    "certificate_bp",
    __name__
)

#admin dashboard
@certificate_bp.route("/admin-dashboard")
@admin_required
def admin_dashboard():

    total_participants = Participant.query.count()

    total_certificates = Certificate.query.count()

    total_verifications = VerificationLog.query.count()

    valid_verifications = VerificationLog.query.filter_by(
        status="valid"
    ).count()

    invalid_verifications = VerificationLog.query.filter_by(
        status="invalid"
    ).count()

    recent_logs = VerificationLog.query.order_by(
        VerificationLog.scan_time.desc()
    ).limit(10).all()

    return render_template(
        "admin_dashboard.html",
        total_participants=total_participants,
        total_certificates=total_certificates,
        total_verifications=total_verifications,
        valid_verifications=valid_verifications,
        invalid_verifications=invalid_verifications,
        recent_logs=recent_logs
    )


# ==================================================
# GENERATE CERTIFICATE
# ==================================================
@certificate_bp.route("/generate-certificate/<int:participant_id>")
@admin_required
def generate_certificate(participant_id):

    participant = Participant.query.get(participant_id)

    if not participant:
        flash("Participant not found", "danger")
        return redirect(url_for("participant_list"))

    existing_cert = Certificate.query.filter_by(
        participant_id=participant_id
    ).first()

    if existing_cert:
        flash("Certificate already exists for this participant", "warning")
        return redirect(url_for("participant_list"))

    certificate_id = str(uuid.uuid4())

    # ================= QR CODE =================
    verify_url = request.host_url.rstrip("/") + f"/verify/{certificate_id}"

    qr = qrcode.make(verify_url)

    os.makedirs("static/qrcodes", exist_ok=True)

    qr_filename = f"{certificate_id}.png"
    qr_full_path = os.path.join("static", "qrcodes", qr_filename)

    qr.save(qr_full_path)

    # ================= SAVE DB =================
    certificate = Certificate(
        id=certificate_id,
        participant_id=participant.id,
        qr_path=f"qrcodes/{qr_filename}"
    )

    db.session.add(certificate)
    db.session.commit()

    # ================= PDF GENERATION =================
    os.makedirs("certificates", exist_ok=True)

    pdf_path = os.path.join("certificates", f"{certificate_id}.pdf")

    pdf = canvas.Canvas(pdf_path, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(170, 750, "CERTIFICATE")

    pdf.setFont("Helvetica", 14)
    pdf.drawString(100, 680, f"Presented To: {participant.name}")
    pdf.drawString(100, 650, f"Email: {participant.email}")
    pdf.drawString(100, 620, f"College: {participant.college}")
    pdf.drawString(100, 590, f"Certificate ID: {certificate_id}")

    pdf.drawImage(qr_full_path, 400, 520, width=120, height=120)

    pdf.save()

    flash("Certificate generated successfully", "success")

    return redirect(
        url_for("certificate_bp.view_certificate", certificate_id=certificate_id)
    )


# ==================================================
# VIEW CERTIFICATE
# ==================================================
@certificate_bp.route("/certificate/<certificate_id>")
def view_certificate(certificate_id):

    certificate = Certificate.query.filter_by(id=certificate_id).first()

    if not certificate:
        flash("Certificate not found", "danger")
        return redirect(url_for("participant_list"))

    return render_template(
        "certificate_view.html",
        certificate=certificate
    )


# ==================================================
# VERIFY CERTIFICATE (ONLY ONE - FIXED)
# ==================================================
@certificate_bp.route("/verify/<certificate_id>")
def verify_certificate(certificate_id):

    certificate = Certificate.query.filter_by(id=certificate_id).first()

    # INVALID CERTIFICATE
    if not certificate:

        log = VerificationLog(
            certificate_id=certificate_id,
            participant_id=None,
            status="invalid",
            ip_address=request.remote_addr,
            device_info=request.user_agent.string
        )

        db.session.add(log)
        db.session.commit()

        return render_template("invalid_certificate.html")

    # VALID CERTIFICATE
    participant = Participant.query.get(certificate.participant_id)

    log = VerificationLog(
        certificate_id=certificate.id,
        participant_id=participant.id if participant else None,
        status="valid",
        ip_address=request.remote_addr,
        device_info=request.user_agent.string
    )

    db.session.add(log)
    db.session.commit()

    return render_template(
        "verify_certificate.html",
        participant=participant,
        certificate=certificate
    )


# ==================================================
# LIST CERTIFICATES
# ==================================================
@certificate_bp.route("/certificates")
@admin_required
def list_certificates():

    certificates = Certificate.query.all()

    return render_template(
        "certificate_list.html",
        certificates=certificates
    )


# ==================================================
# DELETE CERTIFICATE
# ==================================================
@certificate_bp.route(
    "/delete-certificate/<certificate_id>",
    methods=["POST"]
)
@admin_required
def delete_certificate(certificate_id):

    certificate = Certificate.query.filter_by(id=certificate_id).first()

    if not certificate:
        flash("Certificate not found", "danger")
        return redirect(url_for("certificate_bp.list_certificates"))

    db.session.delete(certificate)
    db.session.commit()

    flash("Certificate deleted successfully", "success")

    return redirect(url_for("certificate_bp.list_certificates"))


# ==================================================
# VERIFICATION LOGS
# ==================================================
@certificate_bp.route("/verification-logs")
@admin_required
def verification_logs():

    logs = VerificationLog.query.order_by(
        VerificationLog.scan_time.desc()
    ).all()

    return render_template(
        "verification_logs.html",
        logs=logs
    )


# ==================================================
# EXPORT LOGS (CSV)
# ==================================================
@certificate_bp.route("/export-logs")
def export_logs():

    logs = VerificationLog.query.all()

    def generate():

        yield "ID,Certificate ID,Participant ID,Status,Scan Time,IP Address\n"

        for log in logs:
            yield (
                f"{log.id},"
                f"{log.certificate_id},"
                f"{log.participant_id},"
                f"{log.status},"
                f"{log.scan_time},"
                f"{log.ip_address}\n"
            )

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=verification_logs.csv"
        }
    ) 

@certificate_bp.route("/bulk-upload", methods=["GET", "POST"])
@admin_required
def bulk_upload():

    if request.method == "GET":
        return render_template("bulk_upload.html")

    file = request.files.get("file")

    if not file:
        flash("No file uploaded", "danger")
        return redirect(url_for("certificate_bp.bulk_upload"))

    csv_file = TextIOWrapper(file, encoding="utf-8")
    reader = csv.DictReader(csv_file)

    success_count = 0
    skipped_count = 0

    for row in reader:

        name = row.get("name")
        email = row.get("email")
        college = row.get("college")

        if not name or not email:
            skipped_count += 1
            continue

        # =============================
        # CHECK / CREATE PARTICIPANT
        # =============================
        participant = Participant.query.filter_by(email=email).first()

        if not participant:
            participant = Participant(
                name=name,
                email=email,
                college=college
            )
            db.session.add(participant)
            db.session.commit()

        # =============================
        # CHECK DUPLICATE CERTIFICATE
        # =============================
        existing_cert = Certificate.query.filter_by(
            participant_id=participant.id
        ).first()

        if existing_cert:
            skipped_count += 1
            continue

        # =============================
        # GENERATE CERTIFICATE
        # =============================
        certificate_id = str(uuid.uuid4())

        verify_url = request.host_url.rstrip("/") + f"/verify/{certificate_id}"
        qr = qrcode.make(verify_url)

        os.makedirs("static/qrcodes", exist_ok=True)

        qr_filename = f"{certificate_id}.png"
        qr_path = os.path.join("static", "qrcodes", qr_filename)
        qr.save(qr_path)

        certificate = Certificate(
            id=certificate_id,
            participant_id=participant.id,
            qr_path=f"qrcodes/{qr_filename}"
        )

        db.session.add(certificate)
        db.session.commit()

        # =============================
        # PDF GENERATION
        # =============================
        os.makedirs("certificates", exist_ok=True)

        pdf_path = os.path.join("certificates", f"{certificate_id}.pdf")

        pdf = canvas.Canvas(pdf_path, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawString(170, 750, "CERTIFICATE")

        pdf.setFont("Helvetica", 14)
        pdf.drawString(100, 680, f"Presented To: {participant.name}")
        pdf.drawString(100, 650, f"Email: {participant.email}")
        pdf.drawString(100, 620, f"College: {participant.college}")
        pdf.drawString(100, 590, f"Certificate ID: {certificate_id}")

        pdf.drawImage(qr_path, 400, 520, width=120, height=120)

        pdf.save()

        success_count += 1

    flash(
        f"Bulk upload completed. Success: {success_count}, Skipped: {skipped_count}",
        "success"
    )

    return redirect(url_for("certificate_bp.list_certificates")) 


@certificate_bp.route("/download-certificates-zip")
@admin_required
def download_certificates_zip():

    certificates = Certificate.query.all()

    if not certificates:
        flash("No certificates found", "danger")
        return redirect(url_for("certificate_bp.list_certificates"))

    memory_file = BytesIO()

    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:

        for cert in certificates:

            pdf_path = os.path.join(
                "certificates",
                f"{cert.id}.pdf"
            )

            # Only add if file exists
            if os.path.exists(pdf_path):

                zf.write(
                    pdf_path,
                    arcname=f"{cert.id}.pdf"
                )

    memory_file.seek(0)

    return Response(
        memory_file.getvalue(),
        mimetype="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=certificates.zip"
        }
    ) 
    
@certificate_bp.route("/generate-event-certificates/<int:event_id>")
@admin_required
def generate_event_certificates(event_id):

    event = Event.query.get(event_id)

    if not event:
        flash("Event not found", "danger")
        return redirect(url_for("event_bp.list_events"))

    participants = Participant.query.filter_by(event_id=event_id).all()

    if not participants:
        flash("No participants in this event", "warning")
        return redirect(url_for("event_bp.list_events"))

    success_count = 0
    skipped_count = 0

    for participant in participants:

        # =========================
        # CHECK EXISTING CERTIFICATE
        # =========================
        existing = Certificate.query.filter_by(
            participant_id=participant.id,
            event_id=event_id
        ).first()

        if existing:
            skipped_count += 1
            continue

        # =========================
        # CREATE CERTIFICATE
        # =========================
        certificate_id = str(uuid.uuid4())

        verify_url = request.host_url.rstrip("/") + f"/verify/{certificate_id}"
        qr = qrcode.make(verify_url)

        os.makedirs("static/qrcodes", exist_ok=True)

        qr_filename = f"{certificate_id}.png"
        qr_path = os.path.join("static", "qrcodes", qr_filename)
        qr.save(qr_path)

        certificate = Certificate(
            id=certificate_id,
            participant_id=participant.id,
            event_id=event_id,
            qr_path=f"qrcodes/{qr_filename}"
        )

        db.session.add(certificate)
        db.session.commit()

        # =========================
        # PDF GENERATION
        # =========================
        os.makedirs("certificates", exist_ok=True)

        pdf_path = os.path.join("certificates", f"{certificate_id}.pdf")

        pdf = canvas.Canvas(pdf_path, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawString(170, 750, "CERTIFICATE")

        pdf.setFont("Helvetica", 14)
        pdf.drawString(100, 680, f"Name: {participant.name}")
        pdf.drawString(100, 650, f"Email: {participant.email}")
        pdf.drawString(100, 620, f"Event: {event.name}")
        pdf.drawString(100, 590, f"Certificate ID: {certificate_id}")

        pdf.drawImage(qr_path, 400, 520, width=120, height=120)

        pdf.save()

        success_count += 1

    flash(
        f"Event certificates generated. Success: {success_count}, Skipped: {skipped_count}",
        "success"
    )

    return redirect(url_for("event_bp.list_events"))