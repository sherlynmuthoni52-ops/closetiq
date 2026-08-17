import requests

def get_weather(city, api_key):
    """
    This function contacts the OpenWeatherMap API and
    returns weather data for the given city.

    If the city is not found or there is a connection
    problem it returns None instead of crashing.
    """

    if not api_key:
        return {
            "error": "Weather is not configured. Set the OPENWEATHER_API_KEY environment variable and try again."
        }

    # This is the URL we send our request to
    # We pass the city name, our API key, and units=metric
    # so temperatures come back in Celsius not Fahrenheit
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )

    try:
        # Send the request to OpenWeatherMap
        # This is like the waiter walking to the kitchen
        response = requests.get(url, timeout=5)

        # Check if the request was successful
        # Status code 200 means "OK - everything worked"
        # Status code 404 means "city not found"
        # Status code 401 means "invalid API key"
        if response.status_code == 200:

            # Convert the response into a Python dictionary
            data = response.json()

            # Pull out the specific pieces of information we need
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"].capitalize()
            city_name = data["name"]
            country = data["sys"]["country"]

            # Determine a simple weather category for outfit logic
            # This will be used in Phase 7 to pick appropriate clothes
            if temp < 10:
                weather_category = "Very Cold"
            elif temp < 17:
                weather_category = "Cold"
            elif temp < 24:
                weather_category = "Mild"
            elif temp < 30:
                weather_category = "Warm"
            else:
                weather_category = "Hot"

            # Determine if it is raining
            # This helps suggest appropriate outerwear
            is_raining = "rain" in description.lower() or "drizzle" in description.lower()

            # Return everything as a neat dictionary
            return {
                "city": city_name,
                "country": country,
                "temp": round(temp, 1),
                "feels_like": round(feels_like, 1),
                "humidity": humidity,
                "description": description,
                "category": weather_category,
                "is_raining": is_raining
            }

        elif response.status_code == 404:
            # City name was not recognised
            return {"error": f"City '{city}' not found. Check the spelling and try again."}

        elif response.status_code == 401:
            # API key problem
            return {"error": "Invalid API key. Check your config.py file."}

        else:
            # Some other unexpected problem
            return {"error": f"Weather service returned an unexpected response. Try again later."}

    except requests.exceptions.Timeout:
        # The request took too long
        return {"error": "The weather service took too long to respond. Check your internet connection."}

    except requests.exceptions.ConnectionError:
        # No internet connection
        return {"error": "Could not connect to the weather service. Check your internet connection."}

    except Exception as e:
        # Catch any other unexpected error
        return {"error": f"An unexpected error occurred: {str(e)}"}


def describe_weather_for_outfit(weather):
    """
    Takes a weather dictionary and returns a
    human-readable sentence for the outfit suggestion page.
    """
    if not weather or "error" in weather:
        return ""

    return (
        f"{weather['temp']}°C and {weather['description']} "
        f"in {weather['city']} — feels like {weather['feels_like']}°C"
    )
