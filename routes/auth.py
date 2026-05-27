from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
from models import User
from datetime import datetime

# A Blueprint is a mini section of your app
# All auth-related routes live here
auth_bp = Blueprint("auth", __name__)


# ─── REGISTER ───────────────────────────────────────────
# GET means: show the empty registration form
# POST means: process the form data the user submitted
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # Get the data the user typed into the form
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        # Basic validation
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        # Hash the password — never store plain text passwords
        # generate_password_hash turns "mypassword" into something like
        # "pbkdf2:sha256:260000$abc123..." which cannot be reversed
        hashed_password = generate_password_hash(password)

        # Try to save the user to the database
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                [username, email, hashed_password]
            )
            db.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("auth.login"))

        except Exception:
            # This triggers if username or email already exists
            flash("Username or email already taken. Try another.", "danger")
            return render_template("register.html")

        finally:
            db.close()

    # If it's a GET request just show the empty form
    return render_template("register.html")


# ─── LOGIN ──────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            flash("Please enter your username and password.", "danger")
            return render_template("login.html")

        # Look up the user in the database
        db = get_db()
        user_data = db.execute(
            "SELECT * FROM users WHERE username = ?", [username]
        ).fetchone()
        db.close()

        # Check if user exists AND password matches
        # check_password_hash compares the plain password
        # against the stored hash safely
        if user_data and check_password_hash(user_data["password_hash"], password):
            user = User(user_data["id"], user_data["username"], user_data["email"])
            login_user(user)
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("inventory.dashboard"))
        else:
            flash("Incorrect username or password.", "danger")
            return render_template("login.html")

    return render_template("login.html")


# ─── LOGOUT ─────────────────────────────────────────────
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
