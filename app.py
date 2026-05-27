from flask import Flask
from config import SECRET_KEY, UPLOAD_FOLDER, DATABASE
from database import init_db, get_db
import os

# Create the Flask application
app = Flask(__name__)

# Load settings into the app
app.config["SECRET_KEY"] = SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DATABASE"] = DATABASE

# Make sure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Connect the route files (the different sections of the app)
from routes.auth import auth_bp
from routes.inventory import inventory_bp
from routes.outfit import outfit_bp

app.register_blueprint(auth_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(outfit_bp)

# This runs when you start the app
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
    