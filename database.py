import sqlite3
import os

# This function opens a connection to your database file
def get_db():
    conn = sqlite3.connect("closetiq.db")
    # This line makes results come back as dictionaries
    # so you can say result["username"] instead of result[0]
    conn.row_factory = sqlite3.Row
    return conn

# This function creates all your tables when the app starts
def init_db():
    db = get_db()

    # Create the users table
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # Create the clothing items table
    db.execute("""
        CREATE TABLE IF NOT EXISTS clothing_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            color TEXT,
            size TEXT,
            season TEXT,
            image_path TEXT,
            date_added TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Create the outfit history table
    db.execute("""
        CREATE TABLE IF NOT EXISTS outfit_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            outfit_description TEXT,
            weather_condition TEXT,
            date_generated TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Save the changes and close the connection
    db.commit()
    db.close()
    print("Database tables created successfully!")