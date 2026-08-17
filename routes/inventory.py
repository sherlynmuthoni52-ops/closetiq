from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from database import get_db
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

inventory_bp = Blueprint("inventory", __name__)


# ─── DASHBOARD ──────────────────────────────────────────
@inventory_bp.route("/dashboard")
@login_required
def dashboard():
    db = get_db()

    # Count how many items the user has in each category
    counts = db.execute("""
        SELECT category, COUNT(*) as total
        FROM clothing_items
        WHERE user_id = ?
        GROUP BY category
    """, [current_user.id]).fetchall()

    # Get the 4 most recently added items for a preview
    recent = db.execute("""
        SELECT * FROM clothing_items
        WHERE user_id = ?
        ORDER BY date_added DESC
        LIMIT 4
    """, [current_user.id]).fetchall()

    # Count total items overall
    total = db.execute("""
        SELECT COUNT(*) as total FROM clothing_items
        WHERE user_id = ?
    """, [current_user.id]).fetchone()["total"]

    db.close()

    # Turn the counts into a regular dictionary for easy use in the template
    category_counts = {row["category"]: row["total"] for row in counts}

    return render_template("dashboard.html",
                           category_counts=category_counts,
                           recent_items=recent,
                           total=total)


# ─── VIEW ALL INVENTORY ──────────────────────────────────
@inventory_bp.route("/inventory")
@login_required
def view_inventory():
    # Check if a category filter was applied in the URL
    # e.g. /inventory?category=Tops
    selected_category = request.args.get("category", "All")

    db = get_db()

    if selected_category == "All":
        items = db.execute("""
            SELECT * FROM clothing_items
            WHERE user_id = ?
            ORDER BY date_added DESC
        """, [current_user.id]).fetchall()
    else:
        items = db.execute("""
            SELECT * FROM clothing_items
            WHERE user_id = ? AND category = ?
            ORDER BY date_added DESC
        """, [current_user.id, selected_category]).fetchall()

    db.close()

    categories = ["All", "Tops", "Bottoms", "Footwear", "Accessories"]

    return render_template("inventory.html",
                           items=items,
                           categories=categories,
                           selected_category=selected_category)


# ─── ADD ITEM ────────────────────────────────────────────
@inventory_bp.route("/add-item", methods=["GET", "POST"])
@login_required
def add_item():
    if request.method == "POST":

        # Get all form fields
        name = request.form["name"].strip()
        category = request.form["category"]
        color = request.form["color"].strip()
        size = request.form["size"].strip()
        season = request.form["season"]

        # Validate required fields
        if not name or not category:
            flash("Item name and category are required.", "danger")
            return render_template("add_item.html")

        # Handle the image upload
        image_path = None
        if "image" in request.files:
            file = request.files["image"]

            # Check the file has a name and is an allowed type
            if file.filename != "":
                filename = secure_filename(file.filename)
                allowed = {"png", "jpg", "jpeg", "gif"}
                extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

                if extension in allowed:
                    # Create a unique filename so files never overwrite each other
                    # uuid4() generates a random unique ID like "a3f92b1c-..."
                    unique_name = str(uuid.uuid4()) + "." + extension
                    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
                    file.save(save_path)
                    image_path = unique_name
                else:
                    flash("Only PNG, JPG, JPEG and GIF files are allowed.", "danger")
                    return render_template("add_item.html")

        # Save the item to the database
        db = get_db()
        db.execute("""
            INSERT INTO clothing_items
            (user_id, name, category, color, size, season, image_path, date_added)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            current_user.id,
            name,
            category,
            color,
            size,
            season,
            image_path,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
        db.commit()
        db.close()

        flash(f'"{name}" added to your wardrobe!', "success")
        return redirect(url_for("inventory.view_inventory"))

    return render_template("add_item.html")


# ─── EDIT ITEM ────────────────────────────────────────────
@inventory_bp.route("/edit-item/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    db = get_db()

    # Fetch the item — also check it belongs to the current user
    # This prevents user A from editing user B's items
    item = db.execute("""
        SELECT * FROM clothing_items
        WHERE id = ? AND user_id = ?
    """, [item_id, current_user.id]).fetchone()

    if not item:
        flash("Item not found.", "danger")
        db.close()
        return redirect(url_for("inventory.view_inventory"))

    if request.method == "POST":
        name = request.form["name"].strip()
        category = request.form["category"]
        color = request.form["color"].strip()
        size = request.form["size"].strip()
        season = request.form["season"]

        if not name or not category:
            flash("Item name and category are required.", "danger")
            return render_template("edit_item.html", item=item)

        # Handle new image upload (optional during edit)
        image_path = item["image_path"]
        if "image" in request.files:
            file = request.files["image"]
            if file.filename != "":
                allowed = {"png", "jpg", "jpeg", "gif"}
                filename = secure_filename(file.filename)
                extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
                if extension in allowed:
                    unique_name = str(uuid.uuid4()) + "." + extension
                    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
                    file.save(save_path)
                    image_path = unique_name
                else:
                    flash("Only PNG, JPG, JPEG and GIF files are allowed.", "danger")
                    return render_template("edit_item.html", item=item)

        # Update the record in the database
        db.execute("""
            UPDATE clothing_items
            SET name = ?, category = ?, color = ?, size = ?, season = ?, image_path = ?
            WHERE id = ? AND user_id = ?
        """, [name, category, color, size, season, image_path, item_id, current_user.id])
        db.commit()
        db.close()

        flash(f'"{name}" updated successfully!', "success")
        return redirect(url_for("inventory.view_inventory"))

    db.close()
    return render_template("edit_item.html", item=item)


# ─── DELETE ITEM ──────────────────────────────────────────
@inventory_bp.route("/delete-item/<int:item_id>", methods=["POST"])
@login_required
def delete_item(item_id):
    db = get_db()

    # Again, always check the item belongs to the current user
    item = db.execute("""
        SELECT * FROM clothing_items
        WHERE id = ? AND user_id = ?
    """, [item_id, current_user.id]).fetchone()

    if not item:
        flash("Item not found.", "danger")
        db.close()
        return redirect(url_for("inventory.view_inventory"))

    # Delete the image file from the uploads folder too
    if item["image_path"]:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], item["image_path"])
        if os.path.exists(file_path):
            os.remove(file_path)

    # Delete the record from the database
    db.execute("""
        DELETE FROM clothing_items
        WHERE id = ? AND user_id = ?
    """, [item_id, current_user.id])
    db.commit()
    db.close()

    flash("Item deleted from your wardrobe.", "info")
    return redirect(url_for("inventory.view_inventory"))
