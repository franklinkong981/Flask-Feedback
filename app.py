from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterUserForm, LoginUserForm
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

@app.route("/register", methods=['GET', 'POST'])
def show_register_form():
    """Shows the form that when submitted will register/create a new user. This form accepts a username, password email, first name,
    and last name. If POST, attempts to register the user by adding the enw user to the database, then redirects user to secret page."""
    registerForm = RegisterUserForm()

    if registerForm.validate_on_submit():
        username = registerForm.username.data
        password = registerForm.password.data
        email = registerForm.email.data
        first_name = registerForm.first_name.data
        last_name = registerForm.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        if new_user:
            db.session.add(new_user)
            db.session.commit()
            session['current_user'] = new_user.username
            flash("Welcome! Successfully created account")
            return redirect("/secret")
        else:
            registerForm.username.errors.append('Username already taken. Please pick another')

    return render_template("register.html", form=registerForm)

@app.route("/login", methods=['GET', 'POST'])
def show_login_form():
    """Shows form that when submitted will login a user. This form accepts a username and password. Also contains a link to the register page.
    If POST, attemps to log in the user. If username is found in database and hashed password matches, redirects user to secret page."""
    loginForm = LoginUserForm()

    if loginForm.validate_on_submit():
        username = loginForm.username.data
        password = loginForm.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!")
            session['current_user'] = user.username
            return redirect('/secret')
        else:
            loginForm.username.errors = ['Invalid username/password']
    
    return render_template("login.html", form=loginForm)

@app.route("/secret")
def show_secret():
    if "current_user" not in session:
        flash("Please login first!")
        return redirect('/login')
    return render_template("secret.html")


