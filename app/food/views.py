from flask import Blueprint, request, current_app, render_template, Flask, url_for
from werkzeug.utils import secure_filename
import boto3
import os
import json
import cv2
import numpy as np
import time
import boto3
from tensorflow.keras.models import load_model
from PIL import Image
from . import food
import torch
import numpy as np
import cv2
from ..darknet import *

from ..utils.utils import load_classes
import torchvision.transforms as transforms


configuration_path = "./cfg/yolov3-spp-403cls.cfg"
weights_path = "./weights/last_403food_e200b150v2.pt"
labels = open("./data/403food.names").read().strip().split('\n')

# Setting minimum probability to eliminate weak predictions
probability_minimum = 0.5

# Setting threshold for non maximum suppression
threshold = 0.3
network = Darknet(configuration_path, img_size=416)
network.load_state_dict(torch.load(weights_path, map_location='cpu')['model'], strict=False)
network.eval()

# 이미지 전처리를 위한 트랜스폼 설정
transform = transforms.Compose([
    transforms.Resize((416, 416)),
    transforms.ToTensor(),
])


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


# @food.route("/result", methods = ['GET','POST'])
# def result():
#     global food_weight
#     if request.method == 'POST':
#         food_weight = []
#         for food in products:
#             weight = request.form.get(food)
#             food_weight.append(weight)
#         print(food_weight)
#     return render_template('home/predict.html', products=products, user_image='images/output/' + filename, food_weight=food_weight)


@food.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('./app/static/images/input', filename)
            file.save(file_path)
            
            # 이미지 읽기 및 전처리
            image = Image.open(file_path).convert('RGB')
            img_tensor = transform(image).unsqueeze(0)  # 모델 입력을 위한 텐서로 변환
            
            with torch.no_grad():
                    start = time.time()
                    outputs = network(img_tensor)
                    detection = outputs[0]  # 모델 출력이 튜플일 경우 첫 번째 요소 사용
                    end = time.time()
            
            print(f"YOLO v3 took {end - start:.5f} seconds")

            # 결과 처리
            class_names = []
            boxes = []
            scores = []

            for i in range(detection.size(1)):
                if detection[0, i, 4] > probability_minimum:
                    box = detection[0, i, :4]
                    score = detection[0, i, 4]
                    class_id = torch.argmax(detection[0, i, 5:])
                    class_name = labels[class_id]
                    
                    boxes.append(box.tolist())
                    scores.append(score.item())
                    class_names.append(class_name)

            # Draw boxes and labels on the image
            image_np = np.array(image)
            for box, score, class_name in zip(boxes, scores, class_names):
                x1, y1, x2, y2 = box
                cv2.rectangle(image_np, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                cv2.putText(image_np, f'{class_name}: {score:.2f}', (int(x1), int(y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

            output_file_path = './app/static/images/output/' + filename
            cv2.imwrite(output_file_path, image_np)

            return render_template('home/weights2.html', products=class_names, user_image='images/output/' + filename)

    return render_template('upload_form.html')