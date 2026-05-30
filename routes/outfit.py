from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from database import get_db
from weather import get_weather, describe_weather_for_outfit
from config import WEATHER_API_KEY

outfit_bp = Blueprint("outfit", __name__)


# ─── OUTFIT SUGGESTIONS PAGE ────────────────────────────
@outfit_bp.route("/suggestions", methods=["GET", "POST"])
@login_required
def suggestions():

    weather = None
    weather_summary = ""
    city = ""

    if request.method == "POST":

        # Get the city the user typed in
        city = request.form.get("city", "").strip()

        if not city:
            flash("Please enter a city name.", "danger")
            return render_template("suggestions.html",
                                   weather=None,
                                   weather_summary="",
                                   city="")

        # Call our weather function
        weather = get_weather(city, WEATHER_API_KEY)

        # Check if an error came back
        if "error" in weather:
            flash(weather["error"], "danger")
            return render_template("suggestions.html",
                                   weather=None,
                                   weather_summary="",
                                   city=city)

        # Create a readable summary sentence
        weather_summary = describe_weather_for_outfit(weather)

    return render_template("suggestions.html",
                           weather=weather,
                           weather_summary=weather_summary,
                           city=city)


# ─── OUTFIT HISTORY PAGE ────────────────────────────────
@outfit_bp.route("/history")
@login_required
def history():
    db = get_db()

    records = db.execute("""
        SELECT * FROM outfit_history
        WHERE user_id = ?
        ORDER BY date_generated DESC
    """, [current_user.id]).fetchall()

    db.close()

    return render_template("history.html", records=records)