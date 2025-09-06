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

        # Hash the password before saving
        hashed_password = generate_password_hash(password)

        # Save user into DB
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                       (name, email, hashed_password))
        con.commit()
        cursor.close()
        con.close()

        # Store name in session
        session["name"] = name

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
        cursor.execute("SELECT user_id, name, email, password FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        con.close()

        if user and check_password_hash(user[3], password):
            session["name"] = user[1]  # user[1] = name
            return redirect(url_for("welcome"))

        return "Invalid credentials!"

    return render_template("login.html")


# Welcome route
@app.route("/welcome")
def welcome():
    name = session.get("name", "Guest")
    return render_template("welcome.html", name=name)


# Logout route
@app.route("/logout")
def logout():
    name = session.get("name", "Guest")
    session.clear()
    return render_template("logout.html", name=name)


if __name__ == "__main__":
    app.run(debug=True)
