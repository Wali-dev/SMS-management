from functools import wraps
from bson import ObjectId
from flask import request, jsonify
from config import app, db_mongo, db_SQL
from models import MongoPair, SmsStats, User
from service import SMSService
from werkzeug.utils import secure_filename
import bcrypt
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import random

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALLOWED_EXTENSIONS = {'txt', 'csv'}


# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({"error": "Token is missing!"}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data['user_id']
        except Exception as e:
            return jsonify({"error": str(e)}), 401
        
        return f(current_user, *args, **kwargs)
    return decorator


# Utility functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# User Routes
@app.route("/user/<user_id>", methods=["GET"])
@token_required
def get_user(current_user, user_id):
    try:
        user = User.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return jsonify(User.to_json(user)), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/user", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
    
        if not username or not password or not email:
            return jsonify({"error": "Missing required fields"}), 400
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = User.insert_one(username=username, password=hashed_password, email=email)

        return jsonify({"message": "User created", "userId": str(user_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/signin", methods=["POST"])
def sign_in():
    try:
        data = request.get_json()
        identifier = data.get("identifier")
        password = data.get("password")
        
        if not identifier or not password:
            return jsonify({"error": "Missing required fields"}), 400
        
        user = User.collection.find_one({
            "$or": [
                {"username": identifier},
                {"email": identifier}
            ]
        })
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            token = jwt.encode({
                "user_id": str(user["_id"]),
                "exp": datetime.utcnow() + timedelta(hours=15)
            }, SECRET_KEY, algorithm="HS256")
            
            return jsonify({"token": token}), 200
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Program Routes
@app.route("/program/create", methods=["POST"])
@token_required
def create_program(current_user):
    try:
        if 'number_list' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['number_list']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed. Use .txt or .csv"}), 400

        # Get form data and validate
        pair_name = request.form.get("pair_name")
        proxy = request.form.get("proxy")
        active_status = request.form.get("active_status", "false").lower() == "true"
        priority = int(request.form.get("priority", "0"))
        
        if not all([pair_name, proxy]):
            return jsonify({
                "error": "Missing required fields: pair_name and proxy are required"
            }), 400
            
        # Check existing pair
        existing_pair = MongoPair.collection.find_one({"pair_name": pair_name})
        if existing_pair:
            return jsonify({"error": "Pair with this name already exists"}), 409

        # Process file
        filename = secure_filename(file.filename)
        file_content = file.read()
        file_data = {
            "filename": filename,
            "content": file_content,
            "content_type": file.content_type or "text/plain"
        }
        
        # Create pair
        pair_id = MongoPair.insert_one(
            pair_name=pair_name,
            active_status=active_status,
            priority=priority,
            session_details={},
            proxy=proxy,
            number_list_file=file_data
        )
        
        created_pair = MongoPair.collection.find_one({"_id": pair_id})
        
        return jsonify({
            "message": "Pair created successfully",
            "pair_id": str(pair_id),
            "pair": MongoPair.to_json(created_pair)
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/program/update/<pair_id>", methods=["PATCH"])
@token_required
def update_pair(current_user, pair_id):
    try:
        pair = MongoPair.collection.find_one({"_id": ObjectId(pair_id)})
        if not pair:
            return jsonify({"error": "Pair not found"}), 404

        if not request.is_json:
            return jsonify({"error": "Invalid content type, must be application/json"}), 415
            
        data = request.get_json()
        updatable_fields = ["pair_name", "active_status", "priority", "proxy"]
        update_data = {field: data[field] for field in updatable_fields if field in data}
        
        if "active_status" in update_data:
            update_data["active_status"] = str(update_data["active_status"]).lower() == "true"
        
        MongoPair.collection.update_one(
            {"_id": ObjectId(pair_id)}, 
            {"$set": update_data}
        )
        
        updated_pair = MongoPair.collection.find_one({"_id": ObjectId(pair_id)})
        
        return jsonify({
            "message": "Pair updated successfully",
            "pair": MongoPair.to_json(updated_pair)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/program/delete/<pair_id>", methods=["DELETE"]) 
@token_required
def delete_pair(current_user, pair_id):
    try:
        pair = MongoPair.collection.find_one({"_id": ObjectId(pair_id)})
        if not pair:
            return jsonify({"error": "Pair not found"}), 404
            
        pair_name = pair.get("pair_name")
        
        # Stop running pair if necessary
        if pair_name in SMSService.running_pairs:
            stop_result = SMSService.stop_pair(pair_name)
            if not stop_result["success"]:
                return jsonify({"error": stop_result["message"]}), 400
        
        # Delete SQL stats
        try:
            stats = SmsStats.query.filter_by(pair_name=pair_name).first()
            if stats:
                db_SQL.session.delete(stats)
                db_SQL.session.commit()
        except Exception as e:
            db_SQL.session.rollback()
            return jsonify({"error": f"Failed to delete SMS stats: {str(e)}"}), 500
            
        # Delete MongoDB pair
        delete_result = MongoPair.collection.delete_one({"_id": ObjectId(pair_id)})
        if delete_result.deleted_count == 0:
            return jsonify({"error": "Failed to delete pair"}), 500
            
        return jsonify({
            "message": f"Pair {pair_name} deleted successfully",
            "pair_id": pair_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/program/<operation>", methods=["POST"])
@token_required
def program_operation(current_user, operation):
    try:
        data = request.get_json()
        pair_name = data.get("pair_name")
        
        if not pair_name:
            return jsonify({"error": "Missing pair name"}), 400
        
        pair = MongoPair.collection.find_one({"pair_name": pair_name})
        if not pair:
            return jsonify({"error": "Pair not found"}), 404
            
        operations = {
            "start": SMSService.start_pair,
            "stop": SMSService.stop_pair,
            "restart": SMSService.restart_pair
        }
        
        if operation not in operations:
            return jsonify({"error": "Invalid operation"}), 400
            
        result = operations[operation](pair_name)
        return jsonify(result), 200 if result["success"] else 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/program/pairs", methods=["GET"])
@token_required
def get_all_pairs(current_user):
    try:
        all_pairs = list(MongoPair.collection.find())
        pairs_json = []
        for pair in all_pairs:
            pair_dict = MongoPair.to_json(pair)
            pair_dict["pair_id"] = str(pair["_id"])
            pairs_json.append(pair_dict)
        return jsonify(pairs_json), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Stats Routes
@app.route("/stats/<pair_name>", methods=["GET"])
@token_required
def get_sms_stats(current_user, pair_name):
    try:
        pair = MongoPair.collection.find_one({"pair_name": pair_name})
        if not pair:
            return jsonify({"error": "Pair not found"}), 404

        stats = SmsStats.query.filter_by(pair_name=pair_name).first()
        if not stats:
            return jsonify({"message": "No stats found for this pair", "stats": None}), 404

        stats_dict = {
            "pair_name": stats.pair_name,
            "total_sms_sent": stats.total_sms_sent,
            "total_sms_failed": stats.total_sms_failed,
            "total_rate_of_success": stats.total_rate_of_success,
            "total_rate_of_failure": stats.total_rate_of_failure
        }

        return jsonify({
            "message": "Stats retrieved successfully",
            "stats": stats_dict
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stats/aggregate", methods=["GET"])
@token_required
def get_aggregate_stats(current_user):
    try:
        all_stats = SmsStats.query.all()
        
        if not all_stats:
            return jsonify({
                "message": "No stats found in the database",
                "stats": None
            }), 404
        
        total_sms_sent = sum(stat.total_sms_sent for stat in all_stats)
        total_sms_failed = sum(stat.total_sms_failed for stat in all_stats)
        
        if total_sms_sent > 0:
            overall_success_rate = ((total_sms_sent - total_sms_failed) / total_sms_sent * 100)
            overall_failure_rate = (total_sms_failed / total_sms_sent * 100)
        else:
            overall_success_rate = overall_failure_rate = 0
        
        aggregate_stats = {
            "total_pairs": len(all_stats),
            "total_sms_sent": total_sms_sent,
            "total_sms_failed": total_sms_failed,
            "overall_success_rate": round(overall_success_rate, 2),
            "overall_failure_rate": round(overall_failure_rate, 2)
        }
        
        return jsonify({
            "message": "Aggregate stats retrieved successfully",
            "stats": aggregate_stats
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#fetching dummy stats data into the database, might comment out later
@app.route("/stats/dummy", methods=["POST"])
@token_required
def create_dummy_stats(current_user):
    try:
        data = request.get_json()
        required_fields = ["pair_name", "total_sms_sent", "total_sms_failed"]
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
                
        pair = MongoPair.collection.find_one({"pair_name": data["pair_name"]})
        if not pair:
            return jsonify({"error": "Pair not found in database"}), 404
            
        total_sent = data["total_sms_sent"]
        total_failed = data["total_sms_failed"]
        
        if total_sent < total_failed:
            return jsonify({"error": "total_sms_failed cannot be greater than total_sms_sent"}), 400
            
        success_rate = ((total_sent - total_failed) / total_sent * 100) if total_sent > 0 else 0
        failure_rate = (total_failed / total_sent * 100) if total_sent > 0 else 0
        
        new_stats = SmsStats(
            pair_name=data["pair_name"],
            total_sms_sent=total_sent,
            total_sms_failed=total_failed,
            total_rate_of_success=int(success_rate),
            total_rate_of_failure=int(failure_rate)
        )
        
        existing_stats = SmsStats.query.filter_by(pair_name=data["pair_name"]).first()
        if existing_stats:
            existing_stats.total_sms_sent = total_sent
            existing_stats.total_sms_failed = total_failed
            existing_stats.total_rate_of_success = int(success_rate)
            existing_stats.total_rate_of_failure = int(failure_rate)
        else:
            db_SQL.session.add(new_stats)
        
        db_SQL.session.commit()
        stats_dict = new_stats.to_json() if not existing_stats else existing_stats.to_json()
        
        return jsonify({
            "message": "Stats created successfully",
            "stats": stats_dict
        }), 201
        
    except Exception as e:
        db_SQL.session.rollback()
        return jsonify({"error": str(e)}), 500


# Home Route
@app.route("/", methods=["GET"])
def get_home():
    return "This is the home"


if __name__ == "__main__":
    with app.app_context():
        db_SQL.create_all()
    app.run(debug=True)