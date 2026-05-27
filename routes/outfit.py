from flask import Blueprint, render_template
from flask_login import login_required

outfit_bp = Blueprint("outfit", __name__)

@outfit_bp.route("/suggestions")
@login_required
def suggestions():
    return render_template("suggestions.html")

@outfit_bp.route("/history")
@login_required
def history():
    return render_template("history.html")