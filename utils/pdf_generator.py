import os

from fpdf import FPDF

from utils.qr_generator import generate_qr_code


def generate_certificate(participant):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", "B", 24)

    pdf.cell(
        200,
        20,
        txt="Certificate",
        ln=True,
        align='C'
    )

    pdf.ln(20)

    pdf.set_font("Arial", "", 18)

    pdf.cell(
        200,
        10,
        txt=f"Presented to {participant.name}",
        ln=True,
        align='C'
    )

    # GENERATE QR

    qr_path = generate_qr_code(
        participant.certificate_id
    )

    # ADD QR TO PDF

    pdf.image(
        qr_path,
        x=160,
        y=220,
        w=30
    )

    # CERTIFICATE ID

    pdf.set_font("Arial", "", 10)

    pdf.text(
        140,
        260,
        f"Certificate ID: {participant.certificate_id}"
    )

    # CREATE CERTIFICATES FOLDER

    certificate_folder = "certificates"

    if not os.path.exists(certificate_folder):

        os.makedirs(certificate_folder)

    # OUTPUT PATH

    output_path = (
        f"certificates/{participant.certificate_id}.pdf"
    )

    # SAVE PDF

    pdf.output(output_path)

    return output_path