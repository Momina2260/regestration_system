
import mysql.connector
import os
from flask import request,session, redirect, url_for, render_template,flash
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
class Logic:

    # DB connection
   

    def get_db(self):
     return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    # ------------------ REGISTER --------------------
    def register_user(self, name, email, password, confirm,role):
     if not name or not email or not password or not confirm or not role:
        return "All fields are required!"

     if confirm != password:
        return "Passwords do not match!"
     if len(password)<8:
         return"password should be atleast 8 character !"
     hashed_password = generate_password_hash(password)

     con = self.get_db()
     cursor = con.cursor()
     cursor.execute("SELECT * FROM users WHERE name=%s",(name,))
     if cursor.fetchone()is not None:
        cursor.close()
        con.close()
        return "username already exist please select diffrent!"
     cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
     if cursor.fetchone():
        cursor.close()
        con.close()
        return "Email already exists!"
     if email == "momina2003.uos@gmail.com":
        role = "admin"

     if role not in ["admin","student","teacher"]:
        return "invalid role!"
      
     cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
        (name, email, hashed_password, role)
     )
     con.commit()
     cursor.close()
     con.close()

     return "success"

    # ------------------ LOGIN --------------------
    def login(self, name,email, password):
     con = self.get_db()
     cursor = con.cursor(dictionary=True)

     cursor.execute(
        "SELECT user_id, name, email, password, role FROM users WHERE email=%s LIMIT 1",
        (email,)
     )
     user = cursor.fetchone()
     cursor.execute(
        "SELECT user_id, name, email, password, role FROM users WHERE email=%s LIMIT 1",
        (name,)
     )
     user = cursor.fetchone()

     if user and check_password_hash(user["password"], password):

        cursor.execute(
            "UPDATE users SET last_login = NOW() WHERE user_id=%s",
            (user["user_id"],)
        )
        con.commit()

        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
        session["role"] = user["role"]

        cursor.close()
        con.close()

        flash("Login successful!", "success")
        if user["role"] == "admin":
            return redirect(url_for("routes.welcome"))
        else:
            return redirect(url_for("routes.welcome"))

     cursor.close()
     con.close()
     flash("Invalid email or password!", "danger")
     return redirect(url_for('routes.home', login_required=1))
     # ------------------ DELETE ACCOUNT --------------------
    def delete_account(self):
        con = self.get_db()
        cursor = con.cursor()
        try:
         cursor.execute("DELETE FROM enrollment WHERE user_id=%s", (session["user_id"],))
         cursor.execute("DELETE FROM users WHERE user_id=%s", (session["user_id"],))
         con.commit()
         cursor.close()
         con.close()
         session.clear()
         return redirect(url_for("routes.home"))
       
        except Exception as e:
         con.rollback()
         print("Error:", e)
        finally:
         cursor.close()
         con.close()
    # ------------------ PROFILE --------------------
    def profile(self):
        con = self.get_db()
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, name, email, last_login FROM users WHERE user_id=%s",
            (session["user_id"],)
        )
        user = cursor.fetchone()
        cursor.close()
        con.close()
        return user

    # ------------------ USERS LIST --------------------
    def users_list(self):
        if "role" not in session or session["role"] != "admin":
            return "Access denied!"

        con = self.get_db()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT user_id, name, email FROM users")
        users = cursor.fetchall()
        cursor.close()
        con.close()

        return render_template("users.html", users=users)

    # ------------------ LOGOUT --------------------
    def logout(self):
     name = session.get("name", "Guest")
     session.clear()
     return render_template("logout.html", name=name)

    # ------------------ ENROLL --------------------
  # logic.py
    def enroll(self, course_id):
     con = self.get_db()
     cursor = con.cursor(dictionary=True)

    # Get course info
     cursor.execute("SELECT * FROM courses WHERE course_id=%s", (course_id,))
     course = cursor.fetchone()

     if not course:
        cursor.close()
        con.close()
        return "Course not found."

     if request.method == "POST":
        # user info from session
        user_id = session["user_id"]
        name = session.get("name")
        email = session.get("email")  # optional if needed

        # Check if already enrolled
        cursor.execute(
            "SELECT * FROM Enrollment WHERE user_id=%s AND course_id=%s",
            (user_id, course_id)
        )
        if cursor.fetchone():
            cursor.close()
            con.close()
            return "You are already enrolled in this course!"

        # Insert enrollment
        cursor.execute(
            "INSERT INTO Enrollment (user_id, course_id, enrollment_date) VALUES (%s, %s, CURDATE())",
            (user_id, course_id)
        )
        con.commit()
        cursor.close()
        con.close()

        return f"Enrollment successful! Welcome, {name}, to {course['title']}."

    # GET request → show confirmation page
     cursor.close()
     con.close()
     return render_template("confirm_enroll.html", course=course)
    # ------------------ COURSES --------------------
    def courses(self):
        if "user_id" not in session:
            return redirect(url_for("routes.home"))

        con = self.get_db()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT course_id, title, author, description FROM courses")
        courses = cursor.fetchall()
        cursor.close()
        con.close()

        return render_template("courses.html", courses=courses)

    # ------------------ OPEN COURSE --------------------
    def open_course(self, course_id):
        con = self.get_db()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM courses WHERE course_id=%s", (course_id,))
        course = cursor.fetchone()
        cursor.close()
        con.close()

        return render_template("course_detail.html", course=course)

    # ------------------ ADMIN DASHBOARD --------------------
    def admin_dashboard(self):
        if "role" not in session or session["role"] != "admin":
            return redirect(url_for("routes.login"))

        con = self.get_db()
        cursor = con.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()["total_users"]

        cursor.execute("SELECT COUNT(*) AS total_courses FROM courses")
        total_courses = cursor.fetchone()["total_courses"]

        cursor.execute("SELECT COUNT(*) AS total_enrollments FROM Enrollment")
        total_enrollments = cursor.fetchone()["total_enrollments"]

        cursor.execute("SELECT user_id, name, email, role, last_login FROM users ORDER BY user_id DESC")
        users = cursor.fetchall()

        cursor.execute("SELECT course_id, title, author, description FROM courses ORDER BY course_id DESC")
        courses = cursor.fetchall()

        cursor.execute("""
            SELECT e.en_id, u.name AS student_name, c.title, e.enrollment_date
            FROM Enrollment e
            JOIN users u ON e.user_id = u.user_id
            JOIN courses c ON e.course_id = c.course_id
            ORDER BY e.en_id DESC
        """)
        Enrollment = cursor.fetchall()

        cursor.close()
        con.close()

        return render_template(
            "admin_dashboard.html",
            total_users=total_users,
            total_courses=total_courses,
            total_enrollments=total_enrollments,
            users=users,
            courses=courses,
            Enrollment=Enrollment
        )
    def get_user_enrollments(self,user_id):
       con = self.get_db()
       cursor = con.cursor(dictionary=True)
      
       query = """
        SELECT c.title, c.description, e.enrollment_date
        FROM enrollment e
        JOIN courses c ON e.course_id = c.course_id
        WHERE e.user_id = %s
       """
       cursor.execute(query,(user_id,))
       enrollments=cursor.fetchall()
       cursor.close()
       con.close()
       return enrollments