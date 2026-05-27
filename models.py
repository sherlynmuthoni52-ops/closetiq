from flask_login import UserMixin

# UserMixin gives our User class the methods Flask-Login needs
# like is_authenticated, is_active, get_id
# We get all of that for free by inheriting from UserMixin

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email
