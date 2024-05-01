from flask import render_template, request
from flask_login import login_required, current_user
from datetime import datetime
from datetime import timedelta
from ..record.models import Record
from ..food.models import Food
from ..auth.models import User
from ..extension import db
from . import user

@user.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')


# 날짜별 기록
@user.route('/record')
def record():
    dates = []
    for d in range(0, 7):
        t_date = datetime.today().date()
        p_date = t_date - timedelta(days=d)
        dates.append(p_date)

    record_list = Record.query.filter(Record.user_id==current_user.id, Record.date>=t_date) # 동일한 유저
    
    record_lists = []
    record_id = []
    for i in record_list:
        record_food = Food.query.filter(Food.record_id==i.id)
        record_id.append(i.id)
        record_foods = []
        for r in record_food:
            record_foods.append(r.name)
        record_lists.append(record_foods)

    record_list_food = dict(zip(record_id, record_lists))
    return render_template('record/record.html', record_list=record_list, dates=dates, date=t_date, record_list_food=record_list_food)


@user.route('/day_record/<date>')
def day_record(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d').date() + timedelta(days=1)
    dates = []
    for d in range(0, 7):
        t_date = datetime.today().date()
        p_date = t_date - timedelta(days=d)
        dates.append(p_date)

    record_list = Record.query.filter(Record.user_id==current_user.id, Record.date>=date, Record.date<date_obj)

    record_lists = []
    record_id = []
    for i in record_list:
        record_food = Food.query.filter(Food.record_id==i.id)
        record_id.append(i.id)
        record_foods = []
        for r in record_food:
            record_foods.append(r.name)
        record_lists.append(record_foods)

    record_list_food = dict(zip(record_id, record_lists))
    return render_template('record/record.html', record_list=record_list, dates=dates, date=date, record_list_food=record_list_food)


@user.route('/record/<int:record_id>')
def food_record(record_id):
    food_list = Food.query.filter_by(record_id=record_id)

    food_total = {}
    food_total['calories'] = food_total['sodium'] = food_total['carbohydrate'] \
    = food_total['fat'] = food_total['cholesterol'] = food_total['protein'] = 0
    for food in food_list:
        food_total['calories'] += food.calories
        food_total['sodium'] += food.sodium
        food_total['carbohydrate'] += food.carbohydrate
        food_total['fat'] += food.fat
        food_total['cholesterol'] += food.cholesterol
        food_total['protein'] += food.protein

    record = Record.query.filter(Record.id==record_id).first()

    return render_template('record/food_record.html', food_list=food_list, food_total=food_total, record_image=record.image)


@user.route('/bmi')
def bmi():
    return render_template('user/bmi.html')


@user.route('/bmi/result', methods=['GET', 'POST'])
def bmi_result():
    bmi = ''
    if request.method == 'POST':
        weight = float(request.form.get('weight'))
        height = float(request.form.get('height'))
        bmi = calc_bmi(weight, height)

        user = User.query.get(current_user.id)
        user.weight = weight
        user.height = height
        db.session.commit()

    return render_template("user/bmi_result.html", weight=weight, height=height, bmi=bmi)


def calc_bmi(weight, height):
    return round((weight / ((height / 100) ** 2)), 2)
