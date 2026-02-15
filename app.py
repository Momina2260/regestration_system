import os
from dotenv import load_dotenv
from flask import Flask
from controllers.routes import routes

load_dotenv()  # Load .env file

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True)