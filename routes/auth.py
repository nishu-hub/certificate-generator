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

    # Already logged in
    if "admin_id" in session:
        return redirect(url_for("home_dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()

        password = request.form.get("password", "")

        admin = Admin.query.filter_by(
            username=username
        ).first()

        if admin and check_password_hash(
            admin.password,
            password
        ):

            session["admin_id"] = admin.id

            # RBAC foundation
            session["role"] = "admin"

            flash(
                "Login Successful",
                "success"
            )

            return redirect(
                url_for("home_dashboard")
            )

        flash(
            "Invalid Username or Password",
            "danger"
        )

    return render_template(
        "login.html"
    )


def logout():

    session.clear()

    flash(
        "Logged out successfully",
        "info"
    )

    return redirect(
        url_for("login")
    )