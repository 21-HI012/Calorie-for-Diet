from flask import render_template, Blueprint
from datetime import datetime
from flask_login import current_user
from .record.models import Record

home = Blueprint('home', __name__)

@home.route('/')
def intro():
    return render_template('home/intro.html')


@home.route('/main')
def main():
    t_date = datetime.today().date()
    record_list = Record.query.filter(Record.user_id==current_user.id, Record.date>=t_date).all()
    t_nutrition = {}
    t_nutrition['calories'] = t_nutrition['sodium'] = t_nutrition['carbohydrate'] \
    = t_nutrition['fat'] = t_nutrition['cholesterol'] = t_nutrition['protein'] = 0
    for record in record_list:
        t_nutrition['calories'] += record.t_calories
        t_nutrition['sodium'] += record.t_sodium
        t_nutrition['carbohydrate'] += record.t_carbohydrate
        t_nutrition['fat'] += record.t_fat
        t_nutrition['cholesterol'] += record.t_cholesterol
        t_nutrition['protein'] += record.t_protein

    per_nutrition = {}
    per_nutrition['calories'] = round(t_nutrition['calories']/2100 * 100, 1)

    return render_template('record/main.html', t_nutrition=t_nutrition, t_date=t_date, 
                            per_nutrition=per_nutrition, sodium=t_nutrition['sodium'], carbohydrate=t_nutrition['carbohydrate'],
                            fat=t_nutrition['fat'], cholesterol=t_nutrition['cholesterol'], protein=t_nutrition['protein'])
