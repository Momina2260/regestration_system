from flask import Blueprint, render_template, redirect, url_for, request, session,flash
from services.logic import Logic
from werkzeug.security import generate_password_hash, check_password_hash

routes = Blueprint("routes", __name__)
logic = Logic()

# --------------------- HOME ----------------------
@routes.route("/home")
def home():
    return render_template("home.html")


# --------------------- REGISTER ----------------------

@routes.route("/about")
def about():
    return render_template("about.html")
#----------------------------------------------------
@routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result = logic.register_user(
            name=request.form.get("name"),
            email=request.form.get("email"),
            password=request.form.get("password"),
            confirm=request.form.get("confirm_password")
        )

        if result == "success":
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("routes.login"))
        else:
            flash(result, "danger")  # show error on the form

    return render_template("register.html")

# --------------------- LOGIN ----------------------
@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return logic.login(
            email=request.form.get("email"),
            password=request.form.get("password")
        )
    return render_template("login.html")


# --------------------- DELETE ACCOUNT ----------------------
@routes.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    if "user_id" not in session:
        return redirect(url_for("routes.login"))

    if request.method == "POST":
        return logic.delete_account()
    
    return render_template("delete_account.html")


# --------------------- WELCOME ----------------------
@routes.route("/welcome")
def welcome():
    name = session.get("name", "Guest")
    role = session.get("role", "user")
    return render_template("welcome.html", name=name, role=role)


# --------------------- PROFILE ----------------------
@routes.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("routes.login"))

    user = logic.profile()
    return render_template("profile.html", user=user)


# --------------------- ADMIN USERS LIST ----------------------
@routes.route("/users")
def users_list():
    return logic.users_list()


# --------------------- LOGOUT ----------------------
@routes.route("/logout")
def logout():
    return logic.logout()


# --------------------- ENROLL COURSE ----------------------
# --------------------- ENROLL COURSE ----------------------
@routes.route("/enroll/<int:course_id>", methods=["GET", "POST"])
def enroll(course_id):
    # Call Logic class method
    return logic.enroll(course_id)


# --------------------- COURSES ----------------------
@routes.route("/courses")
def courses():
    return logic.courses()


# --------------------- OPEN COURSE ----------------------
@routes.route("/open_course/<int:course_id>")
def open_course(course_id):
    return logic.open_course(course_id)



# --------------------- ADMIN DASHBOARD ----------------------
@routes.route("/admin")
def admin_dashboard():
    return logic.admin_dashboard()
