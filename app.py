from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterUserForm, LoginUserForm, AddFeedbackForm
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
    if "current_user" in session:
        flash("You're already registered!")
        return redirect(f'/users/{session["current_user"]}')
    
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
            return redirect(f'/users/{session["current_user"]}')
        else:
            registerForm.username.errors.append('Username already taken. Please pick another')

    return render_template("register.html", form=registerForm)

@app.route("/login", methods=['GET', 'POST'])
def show_login_form():
    """Shows form that when submitted will login a user. This form accepts a username and password. Also contains a link to the register page.
    If POST, attemps to log in the user. If username is found in database and hashed password matches, redirects user to secret page."""
    if "current_user" in session:
        flash("You're already logged in!")
        return redirect(f'/users/{session["current_user"]}')
    
    loginForm = LoginUserForm()

    if loginForm.validate_on_submit():
        username = loginForm.username.data
        password = loginForm.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!")
            session['current_user'] = user.username
            return redirect(f'/users/{session["current_user"]}')
        else:
            loginForm.username.errors = ['Invalid username/password']
    
    return render_template("login.html", form=loginForm)

@app.route("/users/<username>")
def show_user_details(username):
    """The main page users are directed to when they are first logged in. Shows all user information except their password. Only logged in 
    users can access this page, and can only see their own page."""
    if "current_user" not in session:
        flash("Please login first to see your user page and feedbacks!")
        return redirect('/login')
    elif username != session['current_user']:
        flash("You can only see information about your own page!")
        return redirect(f'/users/{session["current_user"]}')
    
    user = User.query.get_or_404(session['current_user'])
    return render_template("user_details.html", user=user)

@app.route("/users/<username>/feedback/add", methods=['GET', 'POST'])
def show_add_feedback_form(username):
    """Display a form for a logged in user to add feedback. Makes sure that only logged in users can see this form. 
    If POST, adds the feedback to database as belonging to currently logged in user, then redirects to logged in user's page."""
    if "current_user" not in session:
        flash("Please login first to add feedback")
        return redirect('/login')
    elif username != session['current_user']:
        return redirect(f'/users/{session["current_user"]}/feedback/add')
    
    add_feedback_form = AddFeedbackForm()

    if add_feedback_form.validate_on_submit():
        title = add_feedback_form.title.data
        content = add_feedback_form.content.data

        new_feedback = Feedback(title=title, content=content, username=session['current_user'])
        db.session.add(new_feedback)
        db.session.commit()
        flash('Successfully added feedback')
        return redirect(f'/users/{session["current_user"]}')
    
    return render_template("add_feedback.html", form=add_feedback_form)

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Deletes a user's account as well as each of their tweets. Only a logged in user can delete their own account."""
    if "current_user" not in session:
        flash("Please login first to delete your account")
        return redirect('/login')
    elif username != session['current_user']:
        flash("Nice try hacker, but you can only delete your own account!")
        return redirect(f'/users/{session["current_user"]}')
    
    user_to_delete = User.query.get_or_404(username)
    db.session.delete(user_to_delete)
    db.session.commit()
    session.pop('current_user')

    flash("User successfully deleted!")
    return redirect("/")

@app.route("/feedback/<int:feedback_id>/update", methods=['GET', 'POST'])
def show_update_feedback_form(feedback_id):
    """If GET, show the form to edit a specific feedback by the user. Logged in users can only edit their own feedbacks.
    If POST, update the specific piece of feedback and redirect to the users details page."""
    feedback = Feedback.query.get_or_404(feedback_id)
    if "current_user" not in session:
        flash("Please login first to add/edit your feedbacks")
        return redirect('/login')
    elif feedback.author.username != session['current_user']:
        flash("Sorry! You can't update a feedback that isn't yours")
        return redirect(f'/users/{session["current_user"]}')
    
    edit_feedback_form = AddFeedbackForm(obj=feedback)

    if edit_feedback_form.validate_on_submit():
        feedback.title = edit_feedback_form.title.data
        feedback.content = edit_feedback_form.content.data
        db.session.commit()
        flash(f"Feedback with id {feedback.id} successfully updated!")
        return redirect(f'/users/{session["current_user"]}')
    else:
        return render_template("edit_feedback.html", form=edit_feedback_form)

@app.route("/feedback/<int:feedback_id>/delete", methods=['POST'])
def delete_feedback(feedback_id):
    """Delete a specific feedback and redirect to the logged in user's details page. Ensures that logged in user can only 
    delete their own feedbacks."""
    feedback = Feedback.query.get_or_404(feedback_id)
    if "current_user" not in session:
        flash("Please login first to delete your feedbacks")
        return redirect('/login')
    elif feedback.author.username != session['current_user']:
        flash("Sorry! You can't delete a feedback that isn't yours")
        return redirect(f'/users/{session["current_user"]}')
    
    db.session.delete(feedback)
    db.session.commit()

    flash("Feedback successfully deleted!")
    return redirect(f'/users/{session["current_user"]}')

@app.route("/logout")
def logout():
    """Log out the user and clear any information in the session. Redirects user to home login page."""
    session.pop('current_user')
    return redirect('/')