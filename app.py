from flask import Flask, render_template, redirect, url_for, request, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions

# helper function to get db connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Root@2003",
        database="mydatabase"
    )
@app.route("/home")
def home():
    return render_template("home.html")

# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if confirm != password:
            return "Password does not match, try again!"

        hashed_password = generate_password_hash(password)

        # DB connection
        con = get_db_connection()
        cursor = con.cursor()

        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            con.close()
            return "This email is already registered. Please log in instead."

        # Decide role
        role = "user"
        if email == "momina.uos@gmail.com":
            role = "admin"

        # Save new user
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, role)
        )
        con.commit()
        cursor.close()
        con.close()

        return redirect(url_for("login"))

    return render_template("register.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute(
            "SELECT user_id, name, email, password, role FROM users WHERE email=%s LIMIT 1",
            (email,)
        )
        user = cursor.fetchone()
        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["role"] = user[4]
            return redirect(url_for("welcome"))
            cursor.execute("UPDATE users SET last_login = NOW() WHERE user_id = %s", (user[0],))
            con.commit()
        cursor.close()
        con.close()

       
        return "Invalid credentials!"
       

    return render_template("login.html")

@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # Delete user
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute("DELETE FROM users WHERE user_id=%s", (session["user_id"],))
        con.commit()
        cursor.close()
        con.close()

        session.clear()
        return redirect(url_for("login"))  # redirect after deletion

    # GET → show confirmation page
    return render_template("delete_account.html")

# Welcome route
@app.route("/welcome")
def welcome():
    name = session.get("name", "Guest")
    role = session.get("role", "user")
    return render_template("welcome.html", name=name, role=role)

# Profile route (normal user only)
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute(
        "SELECT user_id, name, email, last_login FROM users WHERE user_id = %s",
        (session["user_id"],)
    )
    user = cursor.fetchone()
    cursor.close()
    con.close()

    return render_template("profile.html", user=user)

# Admin route (all users)
@app.route("/users")
def users_list():
    if "role" not in session or session["role"] != "admin":
        return "Access denied! Admins only."

    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name, email FROM users")
    users = cursor.fetchall()
    cursor.close()
    con.close()

    return render_template("users.html", users=users)

# Logout route
@app.route("/logout")
def logout():
    name = session.get("name", "Guest")
    session.clear()
    return render_template("logout.html", name=name)
@app.route("/enroll/<int:course_id>", methods=["GET", "POST"])
def enroll(course_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    # Fetch course info for display
    cursor.execute("SELECT * FROM courses WHERE course_id = %s", (course_id,))
    course = cursor.fetchone()

    if not course:
        cursor.close()
        con.close()
        return "Course not found."

    # Handle POST request (form submission)
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")

        # Check if already enrolled
        cursor.execute(
            "SELECT * FROM Enrollment WHERE user_id = %s AND course_id = %s",
            (session["user_id"], course_id)
        )
        enrollment = cursor.fetchone()

        if enrollment:
            cursor.close()
            con.close()
            return "You are already enrolled in this course."

        # Insert new enrollment record
        cursor.execute(
            "INSERT INTO Enrollment (user_id, course_id, enrollment_date) VALUES (%s, %s, CURDATE())",
            (session["user_id"], course_id)
        )
        con.commit()

        cursor.close()
        con.close()

        return "Enrollment successful!"

    # Handle GET request (show confirmation form)
    cursor.close()
    con.close()
    return render_template("confirm_enroll.html", course=course)


@app.route("/courses") 
def courses():
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    # Fetch ALL available courses 
    cursor.execute("SELECT course_id, title, author, description FROM courses")
    courses = cursor.fetchall()

    cursor.close()
    con.close()

    return render_template("courses.html", courses=courses)

@app.route("/course/<int:course_id>")
def open_course(course_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM courses WHERE course_id = %s", (course_id,))
    course = cursor.fetchone()
    cursor.close()
    con.close()

    return render_template("course_detail.html", course=course)
@app.route("/admin")#admin dashborad
def admin_dashboard():
    if not is_admin():
        return redirect(url_for("login"))
    
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)

    # Basic stats
    cursor.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cursor.fetchone()["total_users"]

    cursor.execute("SELECT COUNT(*) AS total_courses FROM courses")
    total_courses = cursor.fetchone()["total_courses"]

    cursor.execute("SELECT COUNT(*) AS total_enrollments FROM enrollment")
    total_enrollments = cursor.fetchone()["total_enrollments"]

    cursor.close()
    con.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_courses=total_courses,
        total_enrollments=total_enrollments
    )


if __name__ == "__main__":
    app.run(debug=True)
