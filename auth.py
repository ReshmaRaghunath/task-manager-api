import jwt
import datetime
from flask import request, jsonify
from functools import wraps

SECRET_KEY = "your_super_secret_key"  # Keep this safe in production!

def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if the Authorization header is present
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            # The header format should look like: "Bearer <your_token>"
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            # Decode the token using our secret key
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 401

        # Pass the extracted user_id down to the actual API route function
        return f(current_user_id, *args, **kwargs)
    
    return decorated