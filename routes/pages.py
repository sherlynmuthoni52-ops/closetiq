from flask import Blueprint, redirect, url_for
from flask_login import current_user

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    """Send visitors to the appropriate first screen."""
    if current_user.is_authenticated:
        return redirect(url_for("inventory.dashboard"))
    return redirect(url_for("auth.login"))
