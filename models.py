from flask_login import UserMixin
from . import db
from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    weight = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.Boolean, nullable=True)
    age = db.Column(db.Integer, nullable=True)

    record = relationship("Record", cascade="all, delete", backref="user")

class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    date = db.Column(db.DateTime)

    food = relationship("Food", cascade="all, delete", backref="record")

class Food(db.Model):
    __tablename__ = 'food'
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, ForeignKey('record.id'))
    name = db.Column(db.String(1000))
    calories = db.Column(db.Float)
    sodium = db.Column(db.Float)
    carbohydrate = db.Column(db.Float)
    fat = db.Column(db.Float)
    cholesterol = db.Column(db.Float)
    protein = db.Column(db.Float) 
    