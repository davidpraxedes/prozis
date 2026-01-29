from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """Admin user for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False) # In production use hashed passwords!

class Visitor(db.Model):
    """Tracks a unique visitor session"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False) # UUID from frontend
    ip_address = db.Column(db.String(50))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    current_page = db.Column(db.String(255))
    
    # Relationships
    orders = db.relationship('Order', backref='visitor', lazy=True)
    page_metrics = db.relationship('PageMetric', backref='visitor', lazy=True)

class PageMetric(db.Model):
    """Tracks time spent on each page"""
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitor.id'), nullable=False)
    page_path = db.Column(db.String(255), nullable=False)
    duration_seconds = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    """Stores order details"""
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitor.id'), nullable=True) # Linked to session
    
    # Order Data
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(50), nullable=False) # MBWAY, MULTIBANCO
    status = db.Column(db.String(50), default="PENDING")
    
    # Customer Data (JSON stored as text for flexibility)
    customer_data = db.Column(db.Text) # Stores phone, name, nif, etc.
    
    # Checkouts Data
    checkout_id = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_customer_dict(self):
        try:
            return json.loads(self.customer_data)
        except:
            return {}
