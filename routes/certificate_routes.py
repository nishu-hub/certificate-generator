from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)

from models.models import (
    db,
    Certificate,
    Participant
)

import uuid
import os
import qrcode

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas 


certificate_bp = Blueprint(
    "certificate_bp",
    __name__
)


# ==================================================
# GENERATE CERTIFICATE
# ==================================================

@certificate_bp.route(
    "/generate-certificate/<int:participant_id>"
)
def generate_certificate(participant_id):

    participant = Participant.query.get(participant_id)

    if not participant:

        flash(
            "Participant not found",
            "danger"
        )

        return redirect(
            url_for("participant_list")
        )

    existing_cert = Certificate.query.filter_by(
        participant_id=participant_id
    ).first()

    if existing_cert:

        flash(
            "Certificate already exists for this participant",
            "warning"
        )

        return redirect(
            url_for("participant_list")
        )

    certificate_id = str(
        uuid.uuid4()
    )

    # ==========================================
    # QR CODE GENERATION
    # ==========================================

    verify_url = (
        f"http://127.0.0.1:5000/verify/{certificate_id}"
    )

    qr = qrcode.make(
        verify_url
    )

    os.makedirs(
        "static/qrcodes",
        exist_ok=True
    )

    qr_filename = (
        f"{certificate_id}.png"
    )

    qr_full_path = os.path.join(
        "static",
        "qrcodes",
        qr_filename
    )

    qr.save(
        qr_full_path
    )

    # ==========================================
    # SAVE CERTIFICATE IN DATABASE
    # ==========================================

    certificate = Certificate(
        id=certificate_id,
        participant_id=participant.id,
        qr_path=f"qrcodes/{qr_filename}"
    )

    db.session.add(
        certificate
    )

    db.session.commit()

    # ==========================================
    # PDF GENERATION
    # ==========================================

    os.makedirs(
        "certificates",
        exist_ok=True
    )

    pdf_path = os.path.join(
        "certificates",
        f"{certificate_id}.pdf"
    )

    pdf = canvas.Canvas(
        pdf_path,
        pagesize=letter
    )

    pdf.setFont(
        "Helvetica-Bold",
        24
    )

    pdf.drawString(
        170,
        750,
        "CERTIFICATE"
    )

    pdf.setFont(
        "Helvetica",
        14
    )

    pdf.drawString(
        100,
        680,
        f"Presented To: {participant.name}"
    )

    pdf.drawString(
        100,
        650,
        f"Email: {participant.email}"
    )

    pdf.drawString(
        100,
        620,
        f"College: {participant.college}"
    )

    pdf.drawString(
        100,
        590,
        f"Certificate ID: {certificate_id}"
    )

    pdf.drawImage(
        qr_full_path,
        400,
        520,
        width=120,
        height=120
    )

    pdf.save()

    flash(
        "Certificate generated successfully",
        "success"
    )

    return redirect(
        url_for(
            "certificate_bp.view_certificate",
            certificate_id=certificate_id
        )
    )


# ==================================================
# VIEW CERTIFICATE
# ==================================================

@certificate_bp.route(
    "/certificate/<certificate_id>"
)
def view_certificate(certificate_id):

    certificate = Certificate.query.filter_by(
        id=certificate_id
    ).first()

    if not certificate:

        flash(
            "Certificate not found",
            "danger"
        )

        return redirect(
            url_for("participant_list")
        )

    return render_template(
        "certificate_view.html",
        certificate=certificate
    )


# ==================================================
# VERIFY CERTIFICATE
# ==================================================

@certificate_bp.route(
    "/verify/<certificate_id>"
)
def verify_certificate(certificate_id):

    certificate = Certificate.query.filter_by(
        id=certificate_id
    ).first()

    if not certificate:

        return render_template(
            "result.html",
            valid=False,
            message="Invalid or Fake Certificate"
        )

    return render_template(
        "result.html",
        valid=True,
        certificate=certificate
    )


# ==================================================
# LIST CERTIFICATES
# ==================================================

@certificate_bp.route(
    "/certificates"
)
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
def delete_certificate(certificate_id):

    certificate = Certificate.query.filter_by(
        id=certificate_id
    ).first()

    if not certificate:

        flash(
            "Certificate not found",
            "danger"
        )

        return redirect(
            url_for(
                "certificate_bp.list_certificates"
            )
        )

    db.session.delete(
        certificate
    )

    db.session.commit()

    flash(
        "Certificate deleted successfully",
        "success"
    )

    return redirect(
        url_for(
            "certificate_bp.list_certificates"
        )
    )