from flask import Blueprint, render_template, request
from . import db
from flask_login import login_required, current_user
from .models import *
from datetime import datetime
from datetime import timedelta

user = Blueprint('user', __name__)

@user.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')

# @user.route('/record')
# def record():
#     return render_template('user/record.html')

# 날짜별 기록
@user.route('/record')
def record():
    # user = User.query.get(current_user.id)
    # print(user)

    dates = []
    for d in range(0, 7):
        t_date = datetime.today().date()
        p_date = t_date - timedelta(days=d)
        dates.append(p_date)
    # print(today)

    # record_list = Record.query.filter_by(user_id=current_user.id) # 동일한 유저
    record_list = Record.query.filter(Record.user_id==current_user.id, Record.date>=t_date) # 동일한 유저
    print(record_list)
    # record_list.filter(cast(Record.date, DATE)==date.today()).all() # 같은 날짜
    # print(record_list)

    # food_list = []
    # for record in record_list:
    #     # print(record.id, '\n\n')
    #     food = Food.query.filter_by(record_id=record.id)
    #     food_list += food

    # print("\n\nfood_list:", food_list)
    return render_template('user/record.html', record_list=record_list, dates=dates)

@user.route('/day_record/<date>')
def day_record(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d').date() + timedelta(days=1)
    dates = []
    for d in range(0, 7):
        t_date = datetime.today().date()
        p_date = t_date - timedelta(days=d)
        dates.append(p_date)

    print(type(t_date))
    record_list = Record.query.filter(Record.user_id==current_user.id, Record.date>=date, Record.date<date_obj)
    return render_template('user/record.html', record_list=record_list, dates=dates)

@user.route('/record/<int:record_id>')
def food_record(record_id):
    food_list = Food.query.filter_by(record_id=record_id)

    food_total = {}
    food_total['calories'] = food_total['sodium'] = food_total['carbohydrate'] \
    = food_total['fat'] = food_total['cholesterol'] = food_total['protein'] = 0
    for food in food_list:
        print("\n", food.calories)
        food_total['calories'] += food.calories
        food_total['sodium'] += food.sodium
        food_total['carbohydrate'] += food.carbohydrate
        food_total['fat'] += food.fat
        food_total['cholesterol'] += food.cholesterol
        food_total['protein'] += food.protein

    print(food_total)
    return render_template('user/food_record.html', food_list=food_list, food_total=food_total)

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

