from config import db_SQL, db_mongo
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from bson import Binary
import io

# MySQL Model 2
class SmsStats(db_SQL.Model):
    __tablename__ = "sms_stats"  # Optional table name

    id = db_SQL.Column(db_SQL.Integer, primary_key=True)
    pair_name = db_SQL.Column(db_SQL.String(80), unique=False, nullable=False)
    total_sms_sent = db_SQL.Column(db_SQL.Integer, nullable=False)
    total_sms_failed = db_SQL.Column(db_SQL.Integer, nullable=False)
    total_rate_of_success = db_SQL.Column(db_SQL.Integer, nullable=False)
    total_rate_of_failure = db_SQL.Column(db_SQL.Integer, nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "pairName": self.pair_name,
            "totalSmsSent": self.total_sms_sent,
            "totalSmsFailed": self.total_sms_failed,
            "totalRateOfSuccess": self.total_rate_of_success,
            "totalRateOfFailure": self.total_rate_of_failure,
        }

# MongoDB Model 1
class MongoPair:
    collection = db_mongo["pairs"]  # MongoDB collection name

    @staticmethod
    def to_json(document):
        file_info = document.get("number_list_file", {})
        return {
            "pairName": document.get("pair_name"),
            "activeStatus": document.get("active_status"),
            "priority": document.get("priority"),
            "proxy": document.get("proxy"),
            "sessionDetails": document.get("session_details"),
            "createdAt": document.get("created_at"),
            "numberListFile": {
                "filename": file_info.get("filename"),
                "upload_date": file_info.get("upload_date"),
                "content_type": file_info.get("content_type")
            } if file_info else None
        }

    @classmethod
    def insert_one(cls, pair_name, active_status, priority, session_details, proxy, number_list_file=None):
        data = {
            "pair_name": pair_name,
            "active_status": active_status,
            "proxy": proxy,
            "priority": priority,
            "session_details": session_details,
            "created_at": datetime.utcnow()
        }
        
        if number_list_file:
            data["number_list_file"] = {
                "filename": number_list_file.get("filename"),
                "content": Binary(number_list_file.get("content")),
                "content_type": number_list_file.get("content_type"),
                "upload_date": datetime.utcnow()
            }
        
        result = cls.collection.insert_one(data)
        return result.inserted_id

    @classmethod
    def get_file_content(cls, pair_name):
        pair = cls.collection.find_one({"pair_name": pair_name})
        if pair and "number_list_file" in pair:
            return {
                "content": pair["number_list_file"]["content"],
                "filename": pair["number_list_file"]["filename"],
                "content_type": pair["number_list_file"]["content_type"]
            }
        return None

# MongoDB Model 2 for User
class User:
    collection = db_mongo["users"] 

    collection.create_index("username", unique=True)
    collection.create_index("email", unique=True)

    @staticmethod
    def to_json(document):
        return {
            "username": document.get("username"),
            "password": document.get("password"),
            "email": document.get("email"),
        }

    @classmethod
    def insert_one(cls, username, password, email):
        # Check if username or email already exists
        if cls.collection.find_one({"username": username}):
            raise ValueError("Username already exists")
        if cls.collection.find_one({"email": email}):
            raise ValueError("Email already exists")

        data = {
            "username": username,
            "password": password,
            "email": email
        }
        try:
            result = cls.collection.insert_one(data)
            return result.inserted_id
        except DuplicateKeyError:
            raise ValueError("Duplicate key error: Username or email must be unique")