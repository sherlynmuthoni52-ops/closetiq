import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Environment variables keep deployment-specific secrets out of source control.
SECRET_KEY = os.environ.get("CLOSETIQ_SECRET_KEY", "change-this-before-deploying")
UPLOAD_FOLDER = str(BASE_DIR / "static" / "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
WEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
DATABASE = os.environ.get("CLOSETIQ_DATABASE", str(BASE_DIR / "closetiq.db"))
