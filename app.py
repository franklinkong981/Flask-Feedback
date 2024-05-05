from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db 
# from forms import 
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "oh-so-secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
app.app_context().push()

@app.route("/")
def home():
    """The homepage. Redirects to the login page."""
    return redirect("/login")

@app.route("/login")
def show_login_form():
    """Shows form that when submitted will login a user. This form accepts a username and password. Also contains a link to the register page."""
    return render_template("login.html")

@app.route("/register")
def show_registration_form():
    """Shows the form that when submitted will register/create a new user. This form accepts a username, password email, first name,
    and last name."""
    return render_template("register.html")
