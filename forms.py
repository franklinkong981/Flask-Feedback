from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length

class RegisterUserForm(FlaskForm):
    """Form for registering a user. The new user must enter a username, password, email, first name, and last name."""

    username = StringField("Create a Username", validators=[InputRequired(message="You must provide a username!"), Length(max=20, message="The username can't be longer than 20 characters!")])
    password = PasswordField("Create a Password", validators=[InputRequired(message="You must provide a password!")])
    email = StringField("Enter your Email", validators=[InputRequired(message="You must provide an email address"), Length(max=50, message="The email address can't be longer than 50 characters!")])
    first_name = StringField("Enter your First Name", validators=[InputRequired(message="You must provide your first name"), Length(max=30, message="Your first name can't be more than 30 characters!")])
    last_name = StringField("Enter your Last Name", validators=[InputRequired(message="You must provide a last name"), Length(max=30, message="Your last name can't be more than 30 characters!")])

class LoginUserForm(FlaskForm):
    """Form for logging in a user. The user must supply their username and password."""

    username = StringField("Username", validators=[InputRequired(message="You must enter a username!")])
    password = PasswordField("Password", validators=[InputRequired(message="You must enter a password!")])