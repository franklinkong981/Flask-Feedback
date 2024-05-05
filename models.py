from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to a database."""
    db.app = app
    db.init_app(app)

class User(db.Model):
    """The users that have an account on Flask Feedback. Each user will have a username, a password, email, first_name, and last_name."""

    __tablename__= "users"

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    def get_full_name(self):
        """Returns the first name and last name of the user."""
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Register user with hashed password and return user. If the username is already taken, return false."""
        u = User.query.filter_by(username=username).first()
        if u:
            return False

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user with username and hashed password
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)
    
    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists and password is correct. Return user if valid, else return False."""
        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            # return user instance
            return u
        else:
            return False

class Feedback(db.Model):
    """The Feedback model. Each Feedback has an id, title, content, and username of the user who created it. Each feedback
    belongs to one user, BUT one user can create as many feedbacks as they want."""

    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, db.ForeignKey('users.username'), nullable=False)