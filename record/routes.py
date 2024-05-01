from flask import Response, request, jsonify
from flask_login import current_user
from datetime import datetime
import json
from .models import Record
from ..food.models import Food
from ..user.routes import record as day_record
from ..extension import db
from . import record

@record.route('/barcode_record', methods=['POST'])
def barcode_record():
    data = request.get_json()

    new_record = Record(user_id=current_user.id, date=datetime.now())
    db.session.add(new_record)
    db.session.commit()

    new_food = Food(record_id=new_record.id,
                    name=data['name'],
                    weight=data['weight'],
                    calories=data['calories'], 
                    sodium=data['sodium'], 
                    carbohydrate=data['carbohydrate'], 
                    fat=data['fat'], 
                    cholesterol=data['cholesterol'],
                    protein=data['protein'])
    
    db.session.add(new_food)
    db.session.commit()

    t_record = Record.query.order_by(Record.id.desc()).first()
    t_record.t_calories += new_food.calories
    t_record.t_sodium += new_food.sodium
    t_record.t_carbohydrate += new_food.carbohydrate
    t_record.t_fat += new_food.fat
    t_record.t_cholesterol += new_food.cholesterol
    t_record.t_protein += new_food.protein
    db.session.commit()

    return Response(day_record())


@record.route('/delete_record', methods=['POST'])
def delete_record():
    data = request.get_json()
    record_id = data.get('record_id')
    if not record_id:
        return jsonify({'success': False, 'message': 'No record ID provided'})

    try:
        record = Record.query.get(record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Record not found'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
