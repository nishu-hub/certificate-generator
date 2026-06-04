from flask import render_template, request
from sqlalchemy import or_

from models.models import Participant


def participant_list():

    search = request.args.get(
        "search",
        ""
    )

    if search:

        participants = Participant.query.filter(
            or_(
                Participant.name.contains(search),
                Participant.email.contains(search)
            )
        ).all()

    else:

        participants = Participant.query.all()

    return render_template(
        "participant_list.html",
        participants=participants,
        search=search
    )