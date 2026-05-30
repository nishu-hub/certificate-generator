from flask import render_template, session, redirect, url_for

from models.models import Participant


def participant_list():

    if "admin_id" not in session:

        return redirect(url_for("login"))

    participants = Participant.query.all()

    return render_template(
        "participant_list.html",
        participants=participants
    )