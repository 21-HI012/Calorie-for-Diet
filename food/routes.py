from flask import request, render_template, session, Response, flash, redirect, url_for
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from flask_login import current_user
from datetime import datetime
import boto3
import os
import requests
import json

from . import food
from ..record.models import Record
from ..food.models import Food
from ..extension import db
from ..user.routes import record as day_record
from ..config import Config

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def s3_connection():
    s3 = boto3.client('s3', 
                      aws_access_key_id = Config.AWS_ACCESS_KEY_ID, 
                      aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)
    return s3


def get_nutrition_data(query):
    api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
    api_key = Config.FOOD_API_KEY
    response = requests.get(api_url + query, headers={'X-Api-Key': api_key})
    if response.status_code == 200:
        return response.json()['items']
    else:
        print("Error:", response.status_code, response.text)
        return []


# 이미지 업로드
@food.route("/upload", methods=['GET', 'POST'])
def upload():
    return render_template('food/upload.html')


# 음식 인식
@food.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            session['filename'] = filename

            input_path = f"input/user_{current_user.id}/{filename}"
            output_path = f"user_{current_user.id}/output/{filename}"

            s3 = s3_connection()
            s3.upload_fileobj(file, Config.S3_BUCKET_NAME, input_path)

            file_path = f'https://{Config.S3_BUCKET_NAME}.s3.{Config.AWS_BUCKET_REGION}.amazonaws.com/{input_path}'
            model = YOLO('yolov8n.pt')
            results = model.predict(source=file_path, save=True, project=f"static/images/user_{current_user.id}", name="output", exist_ok=True)

            output_file_path = os.path.join('static/images', f'user_{current_user.id}', 'output', filename)
            s3.upload_file(output_file_path, Config.S3_BUCKET_NAME, output_path)

            os.remove(output_file_path)
            os.remove(os.path.join('', filename))

            with open('allowed_foods.json', 'r') as f:
                allowed_foods_data = json.load(f)
            allowed_foods = allowed_foods_data['foods']

            products = [model.names[int(box.cls)] for box in results[0].boxes if model.names[int(box.cls)] in allowed_foods]
            session['products'] = list(set(products))
            session['user_image'] = f'https://{Config.S3_BUCKET_NAME}.s3.{Config.AWS_BUCKET_REGION}.amazonaws.com/{output_path}'

            if not session['products']:
                return render_template('food/food_notfound.html', user_image=session['user_image'])
            return render_template('food/weights2.html', products=session['products'], user_image=session['user_image'])

    return render_template('food/upload.html')


# 인식 결과
@food.route("/result", methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        food_query = [f"{weight}g {food}" for food, weight in request.form.items() if weight]
        query_string = ' and '.join(food_query)
        nutrition_data = get_nutrition_data(query_string)
        session['nutrition_data'] = nutrition_data
        return render_template('food/predict.html', products=session.get('products', []), user_image=session.get('user_image', ''), nutrition_data=nutrition_data)
    return render_template('food/predict.html', products=session.get('products', []), user_image=session.get('user_image', ''))


# 사용자 음식 입력
@food.route("/input_food", methods=['GET', 'POST'])
def input_food():
    if request.method == 'POST':
        food_names = request.form.getlist('food_names[]')
        if food_names:
            session['products'] = session.get('products', []) + food_names
            return render_template('food/weights2.html', products=session['products'], user_image=session['user_image'])
    return redirect(url_for('upload'))


# 결과 기록
@food.route("/save_result", methods=['POST'])
def save_result():
    nutrition_data = session.get('nutrition_data')
    if nutrition_data:
        new_record = Record(user_id=current_user.id, date=datetime.now(), image=session['user_image'])
        db.session.add(new_record)
        db.session.commit()
        for data in nutrition_data:
            new_food = Food(record_id=new_record.id,
                    name = data['name'],
                    weight = data['serving_size_g'],
                    calories = data['calories'], 
                    sodium = data['sodium_mg'], 
                    carbohydrate = data['carbohydrates_total_g'], 
                    fat = data['fat_total_g'], 
                    cholesterol = data['cholesterol_mg'],
                    protein = data['protein_g'])
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

        session.pop('nutrition_data', None)
        session.pop('user_image', None)        
        return Response(day_record())

    flash('저장할 데이터가 없습니다.', 'info')
    return redirect(url_for('home.main'))