from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import os


def create_app():
    """Initialize and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)
    return app


def init_sql_db(app):
    """Initialize and configure MySQL database connection."""
    try:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQL_DATABASE_URL")
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        
        db_sql = SQLAlchemy(app)
        
        with app.app_context():
            db_sql.engine.connect()
        print("MySQL connected")
        return db_sql
    
    except Exception as e:
        print(f"MySQL connection error: {e}")
        return None


def init_mongo_db():
    """Initialize and configure MongoDB database connection."""
    try:
        mongo_client = MongoClient(os.getenv("MONGODB_DATABASE_URL"))
        db_mongo = mongo_client.get_database()
        print("MongoDB connected")
        return db_mongo
    
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None


def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize Flask app
    app = create_app()
    
    # Initialize databases
    db_sql = init_sql_db(app)
    db_mongo = init_mongo_db()
    
    return app, db_sql, db_mongo


if __name__ == "__main__":
    app, db_sql, db_mongo = main()
    app.run(debug=True)