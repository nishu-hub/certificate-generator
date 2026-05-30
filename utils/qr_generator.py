import qrcode
import os

BASE_URL = "http://127.0.0.1:5000"

def generate_qr_code(certificate_id):

    if not certificate_id:
        raise ValueError("Certificate ID missing")

    # ✅ correct variable usage + consistent base URL
    verification_url = f"{BASE_URL}/verify/{certificate_id}"

    qr = qrcode.make(verification_url)

    qr_folder = "static/qrcodes"

    os.makedirs(qr_folder, exist_ok=True)

    qr_path = os.path.join(qr_folder, f"{certificate_id}.png")

    qr.save(qr_path)

    return qr_path