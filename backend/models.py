from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    data_items = db.relationship('DataItem', backref='user', lazy=True, cascade='all, delete-orphan')
    credentials = db.relationship('Credential', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (without password)"""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DataItem(db.Model):
    """Model for storing general data"""
    __tablename__ = 'data_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    data_type = db.Column(db.String(50), nullable=True)  # e.g., 'note', 'document', 'json'
    extra_data = db.Column(db.JSON, nullable=True)  # Additional structured data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert data item to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'data_type': self.data_type,
            'metadata': self.extra_data,  # Keep 'metadata' in API response for backward compatibility
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Credential(db.Model):
    """Model for storing user credentials (passwords, API keys, etc.)"""
    __tablename__ = 'credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_name = db.Column(db.String(200), nullable=False)  # e.g., 'GitHub', 'AWS'
    username = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    encrypted_password = db.Column(db.String(500), nullable=True)  # Should be encrypted in production
    api_key = db.Column(db.String(500), nullable=True)  # Should be encrypted in production
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert credential to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_name': self.service_name,
            'username': self.username,
            'email': self.email,
            'encrypted_password': self.encrypted_password,  # In production, decrypt before returning
            'api_key': self.api_key,  # In production, decrypt before returning
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
