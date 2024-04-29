from flask import request, current_app, render_template, session, Response
from werkzeug.utils import secure_filename
from . import food
from ultralytics import YOLO
import boto3
import os
import requests
from flask_login import current_user
from datetime import datetime
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

    
@food.route("/upload", methods=['GET', 'POST'])
def upload():
    return render_template('home/upload.html')


@food.route("/result", methods=['GET', 'POST'])
def result():
    global products, filename
    if request.method == 'POST':
        food_query = []
        nutrition_data = {}
        for food, weight in request.form.items():
            if weight:
                food_query.append(f"{weight}g {food}")
            # API 호출을 위한 쿼리 스트링 조합
            query_string = ' and '.join(food_query)

        nutrition_data = get_nutrition_data(query_string)
    
        session['nutrition_data'] = nutrition_data  # 세션 저장

        return render_template('home/predict.html', products=products, user_image=user_image, nutrition_data=nutrition_data)
    else:
        return render_template('home/predict.html', products=products, user_image=user_image)

def get_nutrition_data(query):
    api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
    api_key = Config.FOOD_API_KEY
    response = requests.get(api_url + query, headers={'X-Api-Key': api_key})
    if response.status_code == 200:
        return response.json()['items']
    else:
        print("Error:", response.status_code, response.text)
        return []

@food.route("/predict", methods=['GET', 'POST'])
def predict():
    global products, filename, user_image
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            s3 = s3_connection()
            s3.upload_fileobj(file, Config.S3_BUCKET_NAME, f"input/{filename}")

            file_path = f'https://{Config.S3_BUCKET_NAME}.s3.{Config.AWS_BUCKET_REGION}.amazonaws.com/input/{filename}'

            # YOLOv8로 이미지 읽기 및 예측
            model = YOLO('yolov8n.pt')
            results = model.predict(source=file_path, save=True, project="static/images", name="output", exist_ok=True)

            output_file_path = os.path.join('static/images/output', filename)

            # 결과 s3 업로드
            s3.upload_file(output_file_path, Config.S3_BUCKET_NAME, f"output/{filename}")

            # 로컬 파일 삭제
            os.remove(output_file_path)
            os.remove(os.path.join('', filename))

            products = []
            for box in results[0].boxes:
                cls = box.cls 
                class_label = model.names[int(cls)]
                products.append(class_label)

            products = list(set(products))

            user_image = f'https://{Config.S3_BUCKET_NAME}.s3.{Config.AWS_BUCKET_REGION}.amazonaws.com/output/{filename}'

            return render_template('home/weights2.html', products=products, user_image=user_image)

    return render_template('home/upload.html')


@food.route("/save_result", methods=['POST'])
def save_result():
    nutrition_data = session.get('nutrition_data')  # 세션에서 데이터 가져오기

    new_record = Record(user_id=current_user.id, date=datetime.now(), image = user_image)
    new_record.image = user_image
    db.session.add(new_record)
    db.session.commit()

    if nutrition_data:
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

        return Response(day_record())
    return '저장할 데이터가 없습니다.'
            