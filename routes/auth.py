from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import check_password_hash

from models.models import Admin


def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        admin = Admin.query.filter_by(
            username=username
        ).first()

        if admin and check_password_hash(
            admin.password,
            password
        ):

            session["admin_id"] = admin.id

            flash(
                "Login Successful",
                "success"
            )

            return redirect(url_for("home_dashboard"))

        else:

            flash(
                "Invalid Username or Password",
                "danger"
            )

    return render_template("login.html")


def logout():

    session.clear()

    return redirect(url_for("login"))