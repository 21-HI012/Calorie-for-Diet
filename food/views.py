from flask import request, current_app, render_template, jsonify
from werkzeug.utils import secure_filename
import boto3
import os
import cv2
import json
from ..ai_model.model_label import inputdata
from . import food
import numpy as np
import time
from ultralytics import YOLO
import pandas
import requests


ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class S3Connector:
    def __init__(self, access_key, secret_key, bucket_name):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.bucket_name = bucket_name

    def upload_file_to_s3(self, file, filename):
        object_name = secure_filename(filename)
        self.s3_client.upload_fileobj(file, self.bucket_name, object_name)
        return f"{object_name} has been uploaded to {self.bucket_name}"
    

def allowed_file(filename):
    # 허용된 파일 확장자 체크
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


@food.route('/upload-s3')
def upload_form():
    return render_template('upload_s3.html')


@food.route('/upload-to-s3', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        aws_access_key_id = current_app.config['AWS_ACCESS_KEY_ID']
        aws_secret_access_key = current_app.config['AWS_SECRET_ACCESS_KEY']
        s3_bucket_name = current_app.config['S3_BUCKET_NAME']
        
        s3 = S3Connector(aws_access_key_id, aws_secret_access_key, s3_bucket_name)
        response = s3.upload_file_to_s3(file, filename)
        return response
    
    
@food.route("/upload", methods=['GET', 'POST'])
def upload():
    return render_template('home/upload.html')


@food.route("/result", methods=['GET', 'POST'])
def result():
    global food_weight, products, filename
    if request.method == 'POST':
        food_weight = []
        food_query = []
        nutrition_data = {}
        for food in products:
            weight = request.form.get(food)
            if weight:  # 무게 데이터가 있다면 쿼리 스트링 생성
                food_query.append(f"{weight}g {food}")
            food_weight.append(weight)
        # API 호출을 위한 쿼리 스트링 조합
            query_string = ','.join(food_query)
            nutrition_data[food] = get_nutrition_data(query_string)

        print(nutrition_data)
        return render_template('home/predict.html', products=products, user_image='images/output/' + filename, food_weight=food_weight, nutrition_data=nutrition_data)
    else:
        return render_template('home/predict.html', products=products, user_image='images/output/' + filename)

def get_nutrition_data(query):
    api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
    api_key = 'DAL6Idg3vOt/hviG9ic1Xg==Xc3cWPLf0iuk4v6i'  # 여기에 실제 API 키를 입력하세요.
    response = requests.get(api_url + query, headers={'X-Api-Key': api_key})
    if response.status_code == 200:
        return response.json()['items']
    else:
        print("Error:", response.status_code, response.text)
        return []

@food.route("/predict", methods=['GET', 'POST'])
def predict():
    global products, filename
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('./static/images/input', filename)
            file.save(file_path)

            # YOLOv8로 이미지 읽기 및 예측
            model = YOLO('yolov8n.pt')
            results = model.predict(source=file_path, save=True, project="static/images", name="output", exist_ok=True)
            
            products = []
            for box in results[0].boxes:
                cls = box.cls 
                class_label = model.names[int(cls)]
                products.append(class_label)

            return render_template('home/weights2.html', products=products, user_image='images/output/' + filename)

    return render_template('home/upload.html')
            