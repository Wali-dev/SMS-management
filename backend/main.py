from bson import ObjectId
from flask import request, jsonify
from config import app, db_mongo, db_SQL
from models import Pair, MongoPair, SmsStats, User
import bcrypt
import jwt
import datetime

SECRET_KEY = 'your_secret_key_here'  

def token_required(f):
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

@app.route("/user/<user_id>", methods=["GET"])
@token_required
def get_user(current_user, user_id):
    try:
        user = User.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return jsonify(User.to_json(user)), 200
        else:
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
        
        user = User.collection.find_one({ "$or": [
        {"username": identifier},
        {"email": identifier}
         ]
        })
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            token = jwt.encode({
                "user_id": str(user["_id"]),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=15)
            }, SECRET_KEY, algorithm="HS256")
            
            return jsonify({"token": token}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def get_home():
    return "This is the home"

if __name__ == "__main__":
    with app.app_context():
        db_SQL.create_all()

    app.run(debug=True)
