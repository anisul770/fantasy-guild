from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from dao.user_dao import check_login, create_user
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_value = request.form.get("login_value", "").strip()
        password = request.form.get("password", "").strip()

        if not login_value or not password:
            flash("Please fill in all fields.", "danger")
            return render_template("login.html")

        user_row = check_login(login_value, password)
        if user_row:
            user = User(
                user_row["id"],
                user_row["username"],
                user_row["email"],
                user_row["first_name"],
                user_row["last_name"],
                user_row["role"],
            )
            login_user(user)
            flash("Welcome back!", "success")
            return redirect(url_for("home.index"))

        flash("Wrong username/email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not all([username, email, first_name, last_name, password, confirm_password]):
            flash("Please fill in all fields.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        ok, message = create_user(username, email, first_name, last_name, password)
        flash(message, "success" if ok else "danger")
        if ok:
            return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("home.index"))