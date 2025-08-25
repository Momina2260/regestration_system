from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed to use sessions

@app.route("/home", methods=["GET", "POST"])
def regester():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if confirm != password:
            return "Password does not match, try again!"
                                                         
        # store name in session
        session["name"] = name

        print(f"Registered: {name}, {email}")
        return redirect(url_for("login"))

    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email == "testtest@gmail.com" and password == "1234":
            #  when login successful, redirect to welcome
            return redirect(url_for("welcome"))

        return "Invalid credentials!"

    return render_template("login.html")


@app.route("/welcome")
def welcome():
    #  get name from session (set during register)
    name = session.get("name", "Guest")
    return render_template("welcome.html", name=name)


@app.route("/logout")
def logout():
    name=session.get("name","guest")
    # clear session
    session.clear()
    return render_template("logout.html",name=name)


if __name__ == "__main__":
    app.run(debug=True)
