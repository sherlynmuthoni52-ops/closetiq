# ClosetIQ — Smart Wardrobe Inventory and Outfit Planner

## Project Description
ClosetIQ is a web-based system that allows users to manage their
clothing inventory and receive outfit suggestions based on real-time
weather conditions.

## Technologies Used
- Python 3 with Flask framework
- SQLite database
- HTML5, CSS3, Bootstrap 5
- OpenWeatherMap API
- Flask-Login for authentication

## How to Run the Project

1. Open a terminal in the project folder
2. Activate the virtual environment:
   venv\Scripts\activate
3. Install required packages:
   pip install -r requirements.txt
4. Add your OpenWeatherMap API key to config.py
5. Run the application:
   python app.py
6. Open your browser and go to:
   http://127.0.0.1:5000

## Project Structure
- app.py          → Main application entry point
- config.py       → Application settings
- database.py     → Database connection and table creation
- models.py       → User model for Flask-Login
- weather.py      → OpenWeatherMap API integration
- outfit_engine.py → Rule-based outfit suggestion logic
- routes/         → Page routes and logic
- templates/      → HTML page templates
- static/         → CSS styles and uploaded images

## System Features
- User registration and login with password hashing
- Clothing inventory management with image upload
- Category filtering (Tops, Bottoms, Footwear, Accessories)
- Real-time weather data integration
- Weather-informed outfit suggestions
- Outfit history log

## Developer
[Sherlyn.M]
[250415DIT]
[Africa International University]
[2026]