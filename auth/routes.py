from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from extensions import db, limiter
from models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect_for_role()
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.status == "Active":
            login_user(user)
            return redirect_for_role()
        flash("Invalid credentials or inactive account.", "error")
    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def register():
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        affiliation = "Student"
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Complete all fields. Password must be at least 8 characters.", "error")
        elif User.query.filter_by(email=email).first():
            flash("That email is already registered.", "error")
        else:
            user = User(full_name=name, email=email, affiliation=affiliation, role="user")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created. You can now sign in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html")

@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

def redirect_for_role():
    if current_user.role == "admin":
        return redirect(url_for("admin.overview"))
    if current_user.role == "moderator":
        return redirect(url_for("moderator.queue"))
    return redirect(url_for("student.dashboard"))
