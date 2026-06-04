from functools import wraps

from flask import (
    session,
    redirect,
    url_for,
    flash
)


def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "admin_id" not in session:

            flash(
                "Please login first",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        return f(*args, **kwargs)

    return decorated_function