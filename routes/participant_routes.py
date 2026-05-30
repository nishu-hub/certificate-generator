# ✅ Full fixed participant_routes.py
import csv
from flask import render_template, request, redirect
from models.models import db, Participant


def upload_participants():

    if request.method == "POST":

        file = request.files.get("file")

        if not file:
            return "No file uploaded", 400

        csv_data = file.stream.read().decode("utf-8")

        csv_reader = csv.DictReader(csv_data.splitlines())

        for row in csv_reader:
            participant = Participant(
                name=row.get("name", ""),
                email=row.get("email", ""),
                college=row.get("college", "")
            )
            db.session.add(participant)

        db.session.commit()

        return redirect("/participants")

    return render_template("upload_participants.html")