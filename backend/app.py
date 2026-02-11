from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from flask_cors import CORS
from config import Config
from storage import UserStorage, DataItemStorage, CredentialStorage

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
jwt = JWTManager(app)
CORS(app)  # Enable CORS for frontend integration


# ==================== Authentication Routes ====================


@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username")
        password = data.get("password")

        # Validation
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        # Check if user already exists
        if UserStorage.get_by_username(username):
            return jsonify({"error": "Username already exists"}), 400

        # Create new user
        user = UserStorage.create(username, password)

        # Generate access token
        access_token = create_access_token(identity=user["id"])

        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user": UserStorage.to_dict(user),
                    "access_token": access_token,
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Find user by username
        user = UserStorage.get_by_username(username)

        if not user or not UserStorage.verify_password(user, password):
            return jsonify({"error": "Invalid username or password"}), 401

        # Generate access token
        access_token = create_access_token(identity=user["id"])

        return (
            jsonify(
                {
                    "message": "Login successful",
                    "user": UserStorage.to_dict(user),
                    "access_token": access_token,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current authenticated user"""
    try:
        user_id = get_jwt_identity()
        user = UserStorage.get_by_id(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": UserStorage.to_dict(user)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== Data Storage Routes ====================


@app.route("/api/data", methods=["GET"])
@jwt_required()
def get_data_items():
    """Get all data items for the current user"""
    try:
        user_id = get_jwt_identity()
        data_items = DataItemStorage.get_all(user_id)

        return (
            jsonify(
                {"data_items": [DataItemStorage.to_dict(item) for item in data_items]}
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/data", methods=["POST"])
@jwt_required()
def create_data_item():
    """Create a new data item"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        title = data.get("title")
        if not title:
            return jsonify({"error": "Title is required"}), 400

        data_item = DataItemStorage.create(
            user_id=user_id,
            title=title,
            content=data.get("content"),
            data_type=data.get("data_type"),
            metadata=data.get("metadata"),
        )

        return (
            jsonify(
                {
                    "message": "Data item created successfully",
                    "data_item": DataItemStorage.to_dict(data_item),
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/data/<int:item_id>", methods=["GET"])
@jwt_required()
def get_data_item(item_id):
    """Get a specific data item"""
    try:
        user_id = get_jwt_identity()
        data_item = DataItemStorage.get_by_id(item_id, user_id)

        if not data_item:
            return jsonify({"error": "Data item not found"}), 404

        return jsonify({"data_item": DataItemStorage.to_dict(data_item)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/data/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_data_item(item_id):
    """Update a data item"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        update_data = {}
        if "title" in data:
            update_data["title"] = data["title"]
        if "content" in data:
            update_data["content"] = data["content"]
        if "data_type" in data:
            update_data["data_type"] = data["data_type"]
        if "metadata" in data:
            update_data["metadata"] = data["metadata"]

        data_item = DataItemStorage.update(item_id, user_id, **update_data)

        if not data_item:
            return jsonify({"error": "Data item not found"}), 404

        return (
            jsonify(
                {
                    "message": "Data item updated successfully",
                    "data_item": DataItemStorage.to_dict(data_item),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/data/<int:item_id>", methods=["DELETE"])
@jwt_required()
def delete_data_item(item_id):
    """Delete a data item"""
    try:
        user_id = get_jwt_identity()
        data_item = DataItemStorage.get_by_id(item_id, user_id)

        if not data_item:
            return jsonify({"error": "Data item not found"}), 404

        DataItemStorage.delete(item_id, user_id)

        return jsonify({"message": "Data item deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== Credential Management Routes ====================


@app.route("/api/credentials", methods=["GET"])
@jwt_required()
def get_credentials():
    """Get all credentials for the current user"""
    try:
        user_id = get_jwt_identity()
        credentials = CredentialStorage.get_all(user_id)

        return (
            jsonify(
                {
                    "credentials": [
                        CredentialStorage.to_dict(cred) for cred in credentials
                    ]
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/credentials", methods=["POST"])
@jwt_required()
def create_credential():
    """Create a new credential"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        service_name = data.get("service_name")
        if not service_name:
            return jsonify({"error": "Service name is required"}), 400

        credential = CredentialStorage.create(
            user_id=user_id,
            service_name=service_name,
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),  # In production, encrypt this
            api_key=data.get("api_key"),  # In production, encrypt this
            notes=data.get("notes"),
        )

        return (
            jsonify(
                {
                    "message": "Credential created successfully",
                    "credential": CredentialStorage.to_dict(credential),
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/credentials/<int:credential_id>", methods=["GET"])
@jwt_required()
def get_credential(credential_id):
    """Get a specific credential"""
    try:
        user_id = get_jwt_identity()
        credential = CredentialStorage.get_by_id(credential_id, user_id)

        if not credential:
            return jsonify({"error": "Credential not found"}), 404

        return jsonify({"credential": CredentialStorage.to_dict(credential)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/credentials/<int:credential_id>", methods=["PUT"])
@jwt_required()
def update_credential(credential_id):
    """Update a credential"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        update_data = {}
        if "service_name" in data:
            update_data["service_name"] = data["service_name"]
        if "username" in data:
            update_data["username"] = data["username"]
        if "email" in data:
            update_data["email"] = data["email"]
        if "password" in data:
            update_data["password"] = data["password"]  # In production, encrypt this
        if "api_key" in data:
            update_data["api_key"] = data["api_key"]  # In production, encrypt this
        if "notes" in data:
            update_data["notes"] = data["notes"]

        credential = CredentialStorage.update(credential_id, user_id, **update_data)

        if not credential:
            return jsonify({"error": "Credential not found"}), 404

        return (
            jsonify(
                {
                    "message": "Credential updated successfully",
                    "credential": CredentialStorage.to_dict(credential),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/credentials/<int:credential_id>", methods=["DELETE"])
@jwt_required()
def delete_credential(credential_id):
    """Delete a credential"""
    try:
        user_id = get_jwt_identity()
        credential = CredentialStorage.get_by_id(credential_id, user_id)

        if not credential:
            return jsonify({"error": "Credential not found"}), 404

        CredentialStorage.delete(credential_id, user_id)

        return jsonify({"message": "Credential deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== Health Check ====================


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "API is running"}), 200


# ==================== Initialize Storage ====================

# JSON storage is initialized automatically when storage.py is imported

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
