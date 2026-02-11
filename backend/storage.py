"""
JSON file-based storage system for the Flask API
"""
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path

# Data directory
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# JSON file paths
USERS_FILE = DATA_DIR / "users.json"
DATA_ITEMS_FILE = DATA_DIR / "data_items.json"
CREDENTIALS_FILE = DATA_DIR / "credentials.json"

# Initialize JSON files if they don't exist
def init_storage():
    """Initialize JSON storage files if they don't exist"""
    if not USERS_FILE.exists():
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)
    if not DATA_ITEMS_FILE.exists():
        with open(DATA_ITEMS_FILE, 'w') as f:
            json.dump([], f)
    if not CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump([], f)

# Helper functions
def read_json(file_path):
    """Read JSON file and return data"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_json(file_path, data):
    """Write data to JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def get_next_id(items):
    """Get next available ID from items list"""
    if not items:
        return 1
    return max(item.get('id', 0) for item in items) + 1

# User operations
class UserStorage:
    @staticmethod
    def get_all():
        """Get all users"""
        return read_json(USERS_FILE)
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        users = UserStorage.get_all()
        return next((u for u in users if u.get('id') == user_id), None)
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        users = UserStorage.get_all()
        return next((u for u in users if u.get('username') == username), None)
    
    @staticmethod
    def create(username, password):
        """Create a new user"""
        users = UserStorage.get_all()
        
        # Check if username already exists
        if UserStorage.get_by_username(username):
            raise ValueError("Username already exists")
        
        user_id = get_next_id(users)
        now = datetime.utcnow().isoformat()
        
        user = {
            'id': user_id,
            'username': username,
            'password_hash': generate_password_hash(password),
            'created_at': now,
            'updated_at': now
        }
        
        users.append(user)
        write_json(USERS_FILE, users)
        return user
    
    @staticmethod
    def verify_password(user, password):
        """Verify user password"""
        return check_password_hash(user.get('password_hash'), password)
    
    @staticmethod
    def to_dict(user):
        """Convert user to dictionary (without password)"""
        return {
            'id': user.get('id'),
            'username': user.get('username'),
            'created_at': user.get('created_at'),
            'updated_at': user.get('updated_at')
        }

# DataItem operations
class DataItemStorage:
    @staticmethod
    def get_all(user_id=None):
        """Get all data items, optionally filtered by user_id"""
        items = read_json(DATA_ITEMS_FILE)
        if user_id is not None:
            return [item for item in items if item.get('user_id') == user_id]
        return items
    
    @staticmethod
    def get_by_id(item_id, user_id=None):
        """Get data item by ID, optionally filtered by user_id"""
        items = DataItemStorage.get_all(user_id)
        return next((item for item in items if item.get('id') == item_id), None)
    
    @staticmethod
    def create(user_id, title, content=None, data_type=None, metadata=None):
        """Create a new data item"""
        items = read_json(DATA_ITEMS_FILE)
        item_id = get_next_id(items)
        now = datetime.utcnow().isoformat()
        
        item = {
            'id': item_id,
            'user_id': user_id,
            'title': title,
            'content': content,
            'data_type': data_type,
            'extra_data': metadata,
            'created_at': now,
            'updated_at': now
        }
        
        items.append(item)
        write_json(DATA_ITEMS_FILE, items)
        return item
    
    @staticmethod
    def update(item_id, user_id, **kwargs):
        """Update a data item"""
        items = read_json(DATA_ITEMS_FILE)
        item = DataItemStorage.get_by_id(item_id, user_id)
        
        if not item:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if key == 'metadata':
                item['extra_data'] = value
            elif key in ['title', 'content', 'data_type']:
                item[key] = value
        
        item['updated_at'] = datetime.utcnow().isoformat()
        
        # Update in list
        for i, it in enumerate(items):
            if it.get('id') == item_id and it.get('user_id') == user_id:
                items[i] = item
                break
        
        write_json(DATA_ITEMS_FILE, items)
        return item
    
    @staticmethod
    def delete(item_id, user_id):
        """Delete a data item"""
        items = read_json(DATA_ITEMS_FILE)
        items = [item for item in items if not (item.get('id') == item_id and item.get('user_id') == user_id)]
        write_json(DATA_ITEMS_FILE, items)
        return True
    
    @staticmethod
    def to_dict(item):
        """Convert data item to dictionary"""
        return {
            'id': item.get('id'),
            'user_id': item.get('user_id'),
            'title': item.get('title'),
            'content': item.get('content'),
            'data_type': item.get('data_type'),
            'metadata': item.get('extra_data'),
            'created_at': item.get('created_at'),
            'updated_at': item.get('updated_at')
        }

# Credential operations
class CredentialStorage:
    @staticmethod
    def get_all(user_id=None):
        """Get all credentials, optionally filtered by user_id"""
        credentials = read_json(CREDENTIALS_FILE)
        if user_id is not None:
            return [cred for cred in credentials if cred.get('user_id') == user_id]
        return credentials
    
    @staticmethod
    def get_by_id(credential_id, user_id=None):
        """Get credential by ID, optionally filtered by user_id"""
        credentials = CredentialStorage.get_all(user_id)
        return next((cred for cred in credentials if cred.get('id') == credential_id), None)
    
    @staticmethod
    def create(user_id, service_name, username=None, email=None, password=None, api_key=None, notes=None):
        """Create a new credential"""
        credentials = read_json(CREDENTIALS_FILE)
        credential_id = get_next_id(credentials)
        now = datetime.utcnow().isoformat()
        
        credential = {
            'id': credential_id,
            'user_id': user_id,
            'service_name': service_name,
            'username': username,
            'email': email,
            'encrypted_password': password,  # In production, encrypt this
            'api_key': api_key,  # In production, encrypt this
            'notes': notes,
            'created_at': now,
            'updated_at': now
        }
        
        credentials.append(credential)
        write_json(CREDENTIALS_FILE, credentials)
        return credential
    
    @staticmethod
    def update(credential_id, user_id, **kwargs):
        """Update a credential"""
        credentials = read_json(CREDENTIALS_FILE)
        credential = CredentialStorage.get_by_id(credential_id, user_id)
        
        if not credential:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if key == 'password':
                credential['encrypted_password'] = value
            elif key in ['service_name', 'username', 'email', 'api_key', 'notes']:
                credential[key] = value
        
        credential['updated_at'] = datetime.utcnow().isoformat()
        
        # Update in list
        for i, cred in enumerate(credentials):
            if cred.get('id') == credential_id and cred.get('user_id') == user_id:
                credentials[i] = credential
                break
        
        write_json(CREDENTIALS_FILE, credentials)
        return credential
    
    @staticmethod
    def delete(credential_id, user_id):
        """Delete a credential"""
        credentials = read_json(CREDENTIALS_FILE)
        credentials = [cred for cred in credentials if not (cred.get('id') == credential_id and cred.get('user_id') == user_id)]
        write_json(CREDENTIALS_FILE, credentials)
        return True
    
    @staticmethod
    def to_dict(credential):
        """Convert credential to dictionary"""
        return {
            'id': credential.get('id'),
            'user_id': credential.get('user_id'),
            'service_name': credential.get('service_name'),
            'username': credential.get('username'),
            'email': credential.get('email'),
            'encrypted_password': credential.get('encrypted_password'),
            'api_key': credential.get('api_key'),
            'notes': credential.get('notes'),
            'created_at': credential.get('created_at'),
            'updated_at': credential.get('updated_at')
        }

# Initialize storage on import
init_storage()
