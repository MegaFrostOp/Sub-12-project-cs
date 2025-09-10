import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "Backend is working!"}

if __name__ == "__main__":
    app.run(debug=True)
