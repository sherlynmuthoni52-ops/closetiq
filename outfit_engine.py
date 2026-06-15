import random

def suggest_outfit(items, weather):
    """
    Takes a list of clothing items and a weather dictionary.
    Returns a dictionary containing one suggested item per
    category, chosen based on weather conditions.

    items   → list of clothing items from the database
    weather → dictionary returned by get_weather() in weather.py
    """

    # ── Separate items into their categories ──────────────
    # We go through every item and sort them into four lists
    tops = [i for i in items if i["category"] == "Tops"]
    bottoms = [i for i in items if i["category"] == "Bottoms"]
    footwear = [i for i in items if i["category"] == "Footwear"]
    accessories = [i for i in items if i["category"] == "Accessories"]

    # Get weather details for our decision rules
    category = weather.get("category", "Mild")
    is_raining = weather.get("is_raining", False)
    temp = weather.get("temp", 20)

    # ── Suggest a TOP ─────────────────────────────────────
    top = None

    if category in ["Very Cold", "Cold"]:
        # For cold weather prefer Winter or All season tops
        top = find_item(tops, preferred_seasons=["Winter", "All"])

    elif category == "Mild":
        # For mild weather prefer Spring, Autumn or All season tops
        top = find_item(tops, preferred_seasons=["Spring", "Autumn", "All"])

    else:
        # For warm or hot weather prefer Summer or All season tops
        top = find_item(tops, preferred_seasons=["Summer", "All"])

    # If no season-specific match was found just pick any top
    if not top and tops:
        top = random.choice(tops)

    # ── Suggest BOTTOMS ───────────────────────────────────
    bottom = None

    if category in ["Very Cold", "Cold"]:
        # Prefer Winter or All season bottoms in cold weather
        bottom = find_item(bottoms, preferred_seasons=["Winter", "All"])
    else:
        bottom = find_item(bottoms, preferred_seasons=["Summer", "Spring", "All"])

    # Fallback to any bottom if no season match
    if not bottom and bottoms:
        bottom = random.choice(bottoms)

    # ── Suggest FOOTWEAR ──────────────────────────────────
    shoe = None

    if is_raining:
        # When raining prefer boots or closed shoes
        # We check the item name for keywords
        shoe = find_item_by_name(footwear, keywords=["boot", "rain", "closed"])

    if not shoe and category in ["Very Cold", "Cold"]:
        # Cold weather → prefer boots
        shoe = find_item_by_name(footwear, keywords=["boot", "sneaker"])

    # Fallback to any footwear
    if not shoe and footwear:
        shoe = random.choice(footwear)

    # ── Suggest ACCESSORY ─────────────────────────────────
    accessory = None

    if is_raining:
        # When raining prefer umbrella, raincoat, or jacket
        accessory = find_item_by_name(
            accessories,
            keywords=["umbrella", "rain", "jacket", "coat"]
        )

    if not accessory and category in ["Very Cold", "Cold"]:
        # Cold weather → prefer scarf, hat, gloves, jacket
        accessory = find_item_by_name(
            accessories,
            keywords=["scarf", "hat", "glove", "jacket", "coat", "beanie"]
        )

    # Fallback to any accessory
    if not accessory and accessories:
        accessory = random.choice(accessories)

    # ── Build the result ──────────────────────────────────
    suggestion = {
        "top": top,
        "bottom": bottom,
        "footwear": shoe,
        "accessory": accessory
    }

    return suggestion


def find_item(items, preferred_seasons):
    """
    Goes through a list of items and returns the first one
    whose season matches any of the preferred seasons.
    Returns None if no match is found.
    """
    for item in items:
        if item["season"] in preferred_seasons:
            return item
    return None


def find_item_by_name(items, keywords):
    """
    Goes through a list of items and returns the first one
    whose name contains any of the given keywords.
    The check is case-insensitive so "Boot" matches "boot".
    Returns None if no match is found.
    """
    for item in items:
        item_name = item["name"].lower()
        for keyword in keywords:
            if keyword.lower() in item_name:
                return item
    return None


def build_outfit_description(suggestion, weather):
    """
    Takes a suggestion dictionary and weather dictionary
    and builds a readable text description of the outfit.
    This is what gets saved to the outfit_history table.
    """
    parts = []

    if suggestion.get("top"):
        parts.append(f"Top: {suggestion['top']['name']}")

    if suggestion.get("bottom"):
        parts.append(f"Bottom: {suggestion['bottom']['name']}")

    if suggestion.get("footwear"):
        parts.append(f"Footwear: {suggestion['footwear']['name']}")

    if suggestion.get("accessory"):
        parts.append(f"Accessory: {suggestion['accessory']['name']}")

    # Join all parts with a separator
    description = " | ".join(parts)

    return description


def get_outfit_tip(weather):
    """
    Returns a helpful style tip based on the weather.
    This adds a personal touch to the suggestion page.
    """
    category = weather.get("category", "Mild")
    is_raining = weather.get("is_raining", False)

    if is_raining:
        return "It's raining today — waterproof layers and closed footwear are your best friends! ☔"

    tips = {
        "Very Cold": "Layer up today! Start with a base layer and add a warm coat on top. 🧤",
        "Cold": "A warm mid-layer like a jumper or hoodie will keep you comfortable today. 🧥",
        "Mild": "A great day for smart casual — almost anything in your wardrobe works! 😊",
        "Warm": "Go light today — breathable fabrics will keep you comfortable. 😎",
        "Hot": "Less is more today! Light colours and loose fabrics are ideal. ☀️"
    }

    return tips.get(category, "Dress comfortably and enjoy your day!")
