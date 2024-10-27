from config import db_SQL, db_mongo

# MySQL Model 1
class Pair(db_SQL.Model):
    __tablename__ = "pair"  # Optional table name

    id = db_SQL.Column(db_SQL.Integer, primary_key=True)
    pair_name = db_SQL.Column(db_SQL.String(80), unique=False, nullable=False)
    total_sms_sent = db_SQL.Column(db_SQL.Integer, nullable=False)
    success_rate = db_SQL.Column(db_SQL.Integer, nullable=False)
    failure = db_SQL.Column(db_SQL.Integer, nullable=False)

    # Relationship to SmsStats
    sms_stats = db_SQL.relationship("SmsStats", back_populates="pair", uselist=False)  # One-to-One relationship

    def to_json(self):
        return {
            "id": self.id,
            "pairName": self.pair_name,
            "totalSmsSent": self.total_sms_sent,
            "successRate": self.success_rate,
            "failure": self.failure,
            "smsStats": self.sms_stats.to_json() if self.sms_stats else None,
        }

# MySQL Model 2
class SmsStats(db_SQL.Model):
    __tablename__ = "sms_stats"  # Optional table name

    id = db_SQL.Column(db_SQL.Integer, primary_key=True)
    total_sms_sent = db_SQL.Column(db_SQL.Integer, nullable=False)
    total_sms_failed = db_SQL.Column(db_SQL.Integer, nullable=False)
    total_rate_of_success = db_SQL.Column(db_SQL.Integer, nullable=False)
    total_rate_of_failure = db_SQL.Column(db_SQL.Integer, nullable=False)
    pair_id = db_SQL.Column(db_SQL.Integer, db_SQL.ForeignKey('pair.id'))  # Foreign key to Pair

    # Relationship back to Pair
    pair = db_SQL.relationship("Pair", back_populates="sms_stats")

    def to_json(self):
        return {
            "id": self.id,
            "totalSmsSent": self.total_sms_sent,
            "totalSmsFailed": self.total_sms_failed,
            "totalRateOfSuccess": self.total_rate_of_success,
            "totalRateOfFailure": self.total_rate_of_failure,
            "pairId": self.pair_id,
        }

# MongoDB Model 1
class MongoPair:
    collection = db_mongo["pairs"]  # MongoDB collection name

    @staticmethod
    def to_json(document):
        return {
            "pairName": document.get("pair_name"),
            "activeStatus": document.get("active_status"),
            "priority": document.get("priority"),
            "sessionDetails": document.get("session_details"),
        }

    @classmethod
    def insert_one(cls, pair_name, active_status, priority, session_details):
        data = {
            "pair_name": pair_name,
            "active_status": active_status,
            "priority": priority,
            "session_details": session_details
        }
        result = cls.collection.insert_one(data)
        return result.inserted_id

# MongoDB Model 2 for User
class User:
    collection = db_mongo["users"]  # MongoDB collection name for user data

    @staticmethod
    def to_json(document):
        return {
            "username": document.get("username"),
            "password": document.get("password"),
            "email": document.get("email"),
        }

    @classmethod
    def insert_one(cls, username, password, email):
        data = {
            "username": username,
            "password": password,
            "email": email
        }
        result = cls.collection.insert_one(data)
        return result.inserted_id
