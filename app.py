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

# Route to show available tables (for testing DB connection)
@app.route("/getTables", methods=['GET'])
def get_tables():
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    cursor.close()
    con.close()
    return str(tables)

# Register route
@app.route("/home", methods=["GET", "POST"])
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

    return render_template("home.html")

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
        cursor.close()
        con.close()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["role"] = user[4]
            return redirect(url_for("welcome"))

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
        "SELECT user_id, name, email, role FROM users WHERE user_id=%s",
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
    cursor.execute("SELECT user_id, name, email, role FROM users")
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
@app.route("/enroll")
def enroll():
    if "user_id" not in session:
        return redirect(url_for("login"))

    course_id = request.args.get("course_id")
    if not course_id:
        return "No course selected!"
    try:
      con = get_db_connection()
      cursor = con.cursor()

       # Prevent duplicate enrollment
      cursor.execute(
        "SELECT * FROM Enrollment WHERE user_id=%s AND course_id=%s",
        (session["user_id"], course_id)
      )
      existing = cursor.fetchone()

      if existing:
        cursor.close()
        con.close()
        return "You are already enrolled in this course!"

    # Insert new enrollment
      cursor.execute(
        "INSERT INTO Enrollment (user_id, course_id, enrollment_date) VALUES (%s, %s, CURDATE())",
        (session["user_id"], course_id)
        )
    
    except IntegrityError:
        # Triggered if UNIQUE constraint (user_id, course_id) is violated
     return "You are already enrolled in this course!"

    except Error as e:
        # Handles any other database errors
        return f"Database error: {e}"

    finally:
      con.commit()

      cursor.close()
      con.close()
    return redirect(url_for("courses"))  # redirect to my courses


@app.route("/courses") 
def courses():
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT c.title, c.author, e.enrollment_date
        FROM Enrollment e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.user_id = %s
        """,
        (session["user_id"],)
    )
    courses = cursor.fetchall()
    cursor.close()
    con.close()

    return render_template("courses.html", courses=courses)


if __name__ == "__main__":
    app.run(debug=True)
