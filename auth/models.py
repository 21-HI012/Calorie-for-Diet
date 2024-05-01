from flask_login import UserMixin
from sqlalchemy.orm import relationship
from ..extension import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(256))
    name = db.Column(db.String(1000))
    weight = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.Boolean, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    record = relationship("Record", cascade="all, delete", backref="user")
