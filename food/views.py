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

configuration_path = "./cfg/yolov3.cfg"
weights_path = "./yolov3.weights"

labels = open("./data/coco.names").read().strip().split('\n')

probability_minimum = 0.5
threshold = 0.3
network = cv2.dnn.readNetFromDarknet(configuration_path, weights_path)

layers_names_all = network.getLayerNames()
layers_indexes_output = network.getUnconnectedOutLayers().flatten()
layers_names_output = [layers_names_all[i - 1] for i in layers_indexes_output]

# COCO 데이터셋의 클래스 이름에서 특정 객체의 인덱스 찾기
interested_classes = ['banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake']  # 관심 있는 객체 클래스
class_indexes = [labels.index(cls) for cls in interested_classes if cls in labels]
print("Class indexes of interest:", class_indexes)

colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")


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


@food.route("/result", methods = ['GET','POST'])
def result():
    global food_weight
    if request.method == 'POST':
        food_weight = []
        for food in products:
            weight = request.form.get(food)
            food_weight.append(weight)
        print(food_weight)
    return render_template('home/predict.html', products=products, user_image='images/output/' + filename, food_weight=food_weight)


@food.route("/predict", methods=['GET', 'POST'])
def predict():
    with open('./static/nutrition.json') as f:
        nutrition_data = json.load(f)

    global products, user_image
    if request.method == 'POST':
        file = request.files['file']
        try:
            if file and allowed_file(file.filename):
                global filename
                filename = file.filename
                file_path = os.path.join('./static/images/input', filename)
                file.save(file_path)
                pathImage = file_path
                image_input = cv2.imread(pathImage)
                image_input_shape = image_input.shape
      
                blob = cv2.dnn.blobFromImage(image_input, 1 / 255.0, (416, 416), swapRB=True, crop=False)
                network.setInput(blob)
                start = time.time()
                output_from_network = network.forward(layers_names_output)
                end = time.time()

                bounding_boxes = []
                confidences = []
                class_numbers = []
                h, w = image_input_shape[:2]

                for result in output_from_network:
                    for detection in result:
                        scores = detection[5:]
                        class_current = np.argmax(scores)
                        confidence_current = scores[class_current]

                        # 여기서 특정 클래스만 고려
                        if class_current in class_indexes and confidence_current > probability_minimum:
                            box_current = detection[0:4] * np.array([w, h, w, h])
                            x_center, y_center, box_width, box_height = box_current.astype('int')
                            x_min = int(x_center - (box_width / 2))
                            y_min = int(y_center - (box_height / 2))

                            bounding_boxes.append([x_min, y_min, int(box_width), int(box_height)])
                            confidences.append(float(confidence_current))
                            class_numbers.append(class_current)

                results = cv2.dnn.NMSBoxes(bounding_boxes, confidences, probability_minimum, threshold)
                objects = []

                if len(results) > 0:
                    for i in results.flatten():
                        class_id = class_numbers[i]
                        label = labels[class_id]
                        print(label)
                        objects.append(label)

                        x_min, y_min = bounding_boxes[i][0], bounding_boxes[i][1]
                        box_width, box_height = bounding_boxes[i][2], bounding_boxes[i][3]
                        colour_box_current = [int(j) for j in colors[class_id]]
                        cv2.rectangle(image_input, (x_min, y_min), (x_min + box_width, y_min + box_height),
                                      colour_box_current, 5)
                        text_box_current = '{}: {:.4f}'.format(label, confidences[i])
                        cv2.putText(image_input, text_box_current, (x_min, y_min - 7), cv2.FONT_HERSHEY_SIMPLEX,
                                    1.5, colour_box_current, 5)

                cv2.imwrite('./static/images/output/' + filename, image_input)
                products = list(set(objects))
                return render_template('home/weights2.html', products=products, user_image='images/output/' + filename)

        except Exception as e:
            return "Unable to read the file. Please check if the file extension is correct."

        
# @food.route("/predict", methods=['GET', 'POST'])
# def predict():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file_path = os.path.join('./static/images/input', filename)
#             file.save(file_path)

#             img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)  # 파일 경로에서 직접 이미지를 읽습니다
#             if img is None:
#                 return jsonify({"error": "Failed to read the image"}), 400

#             # 이미지 처리 함수를 호출합니다
#             confidence, label = inputdata(img)  # 수정된 inputdata 함수 호출

#             with open('./foodnames.json', 'r', encoding='utf-8') as file:
#                 food_names = json.load(file)

#             food_name = list(food_names.values())[label]


#             return jsonify({"filename": filename, "confidence": confidence, "label": label, "food_name": food_name})
            