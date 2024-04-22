from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from ..extension import db

class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    date = db.Column(db.DateTime)
    image = db.Column(db.String(100), nullable=True)
    t_calories = db.Column(db.Float, default=0, nullable=True)
    t_sodium = db.Column(db.Float, default=0, nullable=True)
    t_carbohydrate = db.Column(db.Float, default=0, nullable=True)
    t_fat = db.Column(db.Float, default=0, nullable=True)
    t_cholesterol = db.Column(db.Float, default=0, nullable=True)
    t_protein = db.Column(db.Float, default=0, nullable=True)

    food = relationship("Food", cascade="all, delete", backref="record")
