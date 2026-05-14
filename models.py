from datetime import datetime

from flask_login import UserMixin

from extensions import db

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(100),unique=True,nullable=False)
    password = db.Column(db.String(100),nullable=False)
    history = db.relationship("History", backref="user", lazy=True)

class History(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"),nullable=False)
    filename = db.Column(db.String(100),nullable=False)
    type = db.Column(db.String(100),nullable=False)
    result = db.Column(db.String(100),nullable = False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    