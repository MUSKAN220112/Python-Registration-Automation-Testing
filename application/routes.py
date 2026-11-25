from pathlib import Path

from flask import abort, current_app, flash, jsonify, redirect, render_template
from flask import request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash

from database.db_utils import (
    DuplicateEmailError,
    create_user,
    find_user_by_email,
    find_user_by_id,
)
from utilities.dashboard_data import REPORTS_DIR, get_dashboard_data
from utilities.validation import validate_registration


FORM_FIELDS = (
    "first_name", "last_name", "email", "mobile_number", "password",
    "confirm_password", "gender", "date_of_birth", "address", "country",
    "state", "city", "postal_code",
)


def register_routes(app):
    @app.get("/")
    def index():
        if _current_user():
            return redirect(url_for("dashboard"))
        return render_template("login.html", dashboard=get_dashboard_data())

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if _current_user():
            return redirect(url_for("dashboard"))
        if request.method == "GET":
            return render_template("login.html", dashboard=get_dashboard_data())

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = find_user_by_email(app.config["DATABASE_URL"], email)
        if user is None or not check_password_hash(user.password_hash, password):
            return render_template(
                "login.html",
                error="The email address or password is incorrect.",
                email=email,
                dashboard=get_dashboard_data(),
            ), 401

        session.clear()
        session["user_id"] = user.id
        session.permanent = request.form.get("remember_me") == "on"
        return redirect(url_for("dashboard"))

    @app.get("/dashboard")
    def dashboard():
        user = _current_user()
        if user is None:
            return redirect(url_for("login"))
        return render_template(
            "dashboard.html",
            user=user,
            dashboard=get_dashboard_data(),
        )

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/reports/<path:filename>")
    def view_test_report(filename):
        if _current_user() is None:
            return redirect(url_for("login"))
        if Path(filename).name != filename or Path(filename).suffix.lower() != ".html":
            abort(404)

        response = send_from_directory(REPORTS_DIR, filename, mimetype="text/html")
        response.headers["Content-Security-Policy"] = (
            "sandbox allow-scripts allow-same-origin; default-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; img-src 'self' data:"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            if _current_user():
                return redirect(url_for("dashboard"))
            return render_template("register.html")
        data = _registration_data(request.form)
        errors = validate_registration(data)
        if errors:
            return render_template("register.html", errors=errors, form=data), 400
        try:
            create_user(app.config["DATABASE_URL"], data)
        except DuplicateEmailError as error:
            return render_template("register.html", errors={"email": str(error)}, form=data), 409
        flash("Registration successful. Your account has been created.", "success")
        return render_template("register.html", form={}), 200

    @app.post("/api/register")
    def api_register():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"message": "A JSON object is required.", "errors": {}}), 400
        data = _registration_data(payload)
        errors = validate_registration(data)
        if errors:
            return jsonify({"message": "Please correct the registration errors.", "errors": errors}), 400
        try:
            user_id = create_user(app.config["DATABASE_URL"], data)
        except DuplicateEmailError as error:
            return jsonify({"message": str(error), "errors": {"email": str(error)}}), 409
        return jsonify({"message": "Registration successful.", "user_id": user_id}), 201

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200


def _registration_data(source):
    data = {field: str(source.get(field, "") or "").strip() for field in FORM_FIELDS}
    data["password"] = str(source.get("password", "") or "")
    data["confirm_password"] = str(source.get("confirm_password", "") or "")
    data["terms_accepted"] = source.get("terms_accepted") in (True, "true", "on", "1", 1)
    return data


def _current_user():
    user_id = session.get("user_id")
    if not isinstance(user_id, int):
        return None

    user = find_user_by_id(current_app.config["DATABASE_URL"], user_id)
    if user is None:
        session.clear()
    return user
