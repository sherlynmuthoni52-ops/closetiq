from flask import Blueprint, render_template
from flask_login import login_required, current_user

inventory_bp = Blueprint("inventory", __name__)

@inventory_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@inventory_bp.route("/inventory")
@login_required
def view_inventory():
    return render_template("inventory.html")
