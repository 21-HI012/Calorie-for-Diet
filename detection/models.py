from sqlalchemy import ForeignKey
from ..extension import db

class Food(db.Model):
    __tablename__ = 'food'
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, ForeignKey('record.id'))
    name = db.Column(db.String(1000))
    weight = db.Column(db.Integer, default=100, nullable=True)
    calories = db.Column(db.Float)
    sodium = db.Column(db.Float)
    carbohydrate = db.Column(db.Float)
    fat = db.Column(db.Float)
    cholesterol = db.Column(db.Float)
    protein = db.Column(db.Float) 
