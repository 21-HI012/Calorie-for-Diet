from flask import Response
from flask_login import current_user
from datetime import datetime
import json
from .models import Record
from ..detection.models import Food
from ..user.routes import record as day_record
from ..extension import db
from . import record

@record.route('/barcode_record/<my_code>')
def barcode_record(my_code):
    with open('./static/food.json') as f:
        food_data = json.load(f)

    new_record = Record(user_id=current_user.id, date=datetime.now())
    db.session.add(new_record)
    db.session.commit()
    
    for i in food_data['food']:
        if i['barcode'] == my_code:
            new_food = Food(record_id=new_record.id,
                            name=i['name'],
                            weight=i['weight'],
                            calories=i['calories'], 
                            sodium=i['sodium'], 
                            carbohydrate=i['carbohydrate'], 
                            fat=i['fat'], 
                            cholesterol=i['cholesterol'],
                            protein=i['protein'])

            db.session.add(new_food)
            db.session.commit()

            t_record = Record.query.order_by(Record.id.desc()).first()
            t_record.t_calories += i['calories']
            t_record.t_sodium += i['sodium']
            t_record.t_carbohydrate += i['carbohydrate']
            t_record.t_fat += i['fat']
            t_record.t_cholesterol += i['cholesterol']
            t_record.t_protein += i['protein']
            db.session.commit()

    return Response(day_record())
