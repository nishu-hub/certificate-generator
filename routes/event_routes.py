from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.models import db, Event
from utils.decorators import admin_required

event_bp = Blueprint("event_bp", __name__)

@event_bp.route("/create-event", methods=["GET", "POST"])
@admin_required
def create_event():

    if request.method == "POST":

        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            flash("Event name required", "danger")
            return redirect(url_for("event_bp.create_event"))

        event = Event(
            name=name,
            description=description
        )

        db.session.add(event)
        db.session.commit()

        flash("Event created successfully", "success")
        return redirect(url_for("event_bp.list_events"))

    return render_template("create_event.html") 

@event_bp.route("/events")
@admin_required
def list_events():

    events = Event.query.all()

    return render_template(
        "events.html",
        events=events
    ) 