from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

# Environment variables
SQL = os.getenv("SQL_DATABASE_URL")
MONGODB = os.getenv("MONGODB_DATABASE_URL")

app = Flask(__name__)
CORS(app)

# MySQL Database Configuration
try:
    app.config["SQLALCHEMY_DATABASE_URI"] = SQL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db_SQL = SQLAlchemy(app)
    with app.app_context():
        db_SQL.engine.connect()
    print("MySQL connected")
except Exception as e:
    print(f"MySQL connection error: {e}")

# MongoDB Database Configuration
try:
    mongo_client = MongoClient(MONGODB)
    db_mongo = mongo_client.get_database()  # Access the MongoDB database instance
    print("MongoDB connected")
except Exception as e:
    print(f"MongoDB connection error: {e}")

if __name__ == "__main__":
    app.run(debug=True)