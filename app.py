from flask import Flask
from flask_login import LoginManager
from config import SECRET_KEY, UPLOAD_FOLDER, DATABASE
from database import init_db
import os

# Create the Flask application
app = Flask(__name__)

# Load settings into the app
app.config["SECRET_KEY"] = SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DATABASE"] = DATABASE

# Make sure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set up Flask-Login
login_manager = LoginManager(app)

# If someone tries to visit a protected page without
# logging in, send them to the login page
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."

# This function tells Flask-Login how to find a user by their ID
# It runs automatically every time a logged-in user loads a page
@login_manager.user_loader
def load_user(user_id):
    from models import User
    from database import get_db
    db = get_db()
    user_data = db.execute(
        "SELECT * FROM users WHERE id = ?", [user_id]
    ).fetchone()
    db.close()
    if user_data:
        return User(user_data["id"], user_data["username"], user_data["email"])
    return None

# Connect the route files
from routes.auth import auth_bp
from routes.inventory import inventory_bp
from routes.outfit import outfit_bp
from routes.pages import pages_bp

app.register_blueprint(auth_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(outfit_bp)
app.register_blueprint(pages_bp)

# This runs when you start the app
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
    