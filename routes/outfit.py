from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from database import get_db
from weather import get_weather, describe_weather_for_outfit
from outfit_engine import suggest_outfit, build_outfit_description, get_outfit_tip
from config import WEATHER_API_KEY
from datetime import datetime

outfit_bp = Blueprint("outfit", __name__)


# ─── OUTFIT SUGGESTIONS PAGE ────────────────────────────
@outfit_bp.route("/suggestions", methods=["GET", "POST"])
@login_required
def suggestions():

    weather = None
    weather_summary = ""
    city = ""
    suggestion = None
    outfit_tip = ""
    has_items = False

    # Check if the user has any clothing items at all
    db = get_db()
    item_count = db.execute("""
        SELECT COUNT(*) as total FROM clothing_items
        WHERE user_id = ?
    """, [current_user.id]).fetchone()["total"]
    db.close()

    has_items = item_count > 0

    if request.method == "POST":

        city = request.form.get("city", "").strip()

        if not city:
            flash("Please enter a city name.", "danger")
            return render_template("suggestions.html",
                                   weather=None,
                                   suggestion=None,
                                   weather_summary="",
                                   outfit_tip="",
                                   city="",
                                   has_items=has_items)

        # Step 1: Get the weather
        weather = get_weather(city, WEATHER_API_KEY)

        if "error" in weather:
            flash(weather["error"], "danger")
            return render_template("suggestions.html",
                                   weather=None,
                                   suggestion=None,
                                   weather_summary="",
                                   outfit_tip="",
                                   city=city,
                                   has_items=has_items)

        weather_summary = describe_weather_for_outfit(weather)
        outfit_tip = get_outfit_tip(weather)

        # Step 2: Get all the user's clothing items from the database
        db = get_db()
        items = db.execute("""
            SELECT * FROM clothing_items
            WHERE user_id = ?
        """, [current_user.id]).fetchall()

        # Convert to list of regular dictionaries so outfit engine can use them
        items_list = [dict(item) for item in items]

        # Step 3: Generate the outfit suggestion
        if items_list:
            suggestion = suggest_outfit(items_list, weather)

            # Step 4: Save this suggestion to the outfit history
            description = build_outfit_description(suggestion, weather)
            weather_condition = f"{weather['category']} - {weather['temp']}°C in {weather['city']}"

            db.execute("""
                INSERT INTO outfit_history
                (user_id, outfit_description, weather_condition, date_generated)
                VALUES (?, ?, ?, ?)
            """, [
                current_user.id,
                description,
                weather_condition,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            db.commit()

        db.close()

    return render_template("suggestions.html",
                           weather=weather,
                           suggestion=suggestion,
                           weather_summary=weather_summary,
                           outfit_tip=outfit_tip,
                           city=city,
                           has_items=has_items)


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