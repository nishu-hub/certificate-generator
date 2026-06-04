import csv
import re

from flask import (
    render_template,
    request,
    redirect,
    flash
) 

from flask import Response 

from models.models import (
    db,
    Participant
)


# ==========================================
# EMAIL VALIDATION
# ==========================================

def is_valid_email(email):

    pattern = r"^[^@]+@[^@]+\.[^@]+$"

    return re.match(pattern, email)


# ==========================================
# UPLOAD PARTICIPANTS
# ==========================================

def upload_participants():

    if request.method == "POST":

        file = request.files.get("file")

        if not file:

            flash(
                "No file uploaded",
                "danger"
            )

            return redirect(request.url)

        if not file.filename.lower().endswith(".csv"):

            flash(
                "Only CSV files are allowed",
                "danger"
            )

            return redirect(request.url)

        try:

            csv_data = file.stream.read().decode(
                "utf-8"
            )

            csv_reader = csv.DictReader(
                csv_data.splitlines()
            )

            added_count = 0
            skipped_count = 0

            for row in csv_reader:

                name = row.get(
                    "name",
                    ""
                ).strip()

                email = row.get(
                    "email",
                    ""
                ).strip()

                college = row.get(
                    "college",
                    ""
                ).strip()

                # Skip empty rows
                if not name or not email:

                    skipped_count += 1
                    continue

                # Validate email
                if not is_valid_email(email):

                    skipped_count += 1
                    continue

                # Prevent duplicate emails
                existing_participant = Participant.query.filter_by(
                    email=email
                ).first()

                if existing_participant:

                    skipped_count += 1
                    continue

                participant = Participant(
                    name=name,
                    email=email,
                    college=college
                )

                db.session.add(
                    participant
                )

                added_count += 1

            db.session.commit()

            flash(
                f"{added_count} participants uploaded successfully. "
                f"{skipped_count} rows skipped.",
                "success"
            )

            return redirect(
                "/participants"
            )

        except Exception as e:

            db.session.rollback()

            flash(
                f"Upload failed: {str(e)}",
                "danger"
            )

            return redirect(
                request.url
            )

    return render_template(
        "upload_participants.html"
    ) 
    
def export_participants():

    participants = Participant.query.all()

    def generate():

        yield "ID,Name,Email,College\n"

        for p in participants:
            yield (
                f"{p.id},"
                f"{p.name},"
                f"{p.email},"
                f"{p.college}\n"
            )

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=participants.csv"
        }
    )