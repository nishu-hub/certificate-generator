from app import app

from models.models import db, Event


with app.app_context():

    event = Event(

        title="Python Workshop",

        date="29 May 2026",

        organizer="ABC Engineering College"
    )

    db.session.add(event)

    db.session.commit()

    print("Event Added Successfully")