from flask import request, current_app, render_template, jsonify
from werkzeug.utils import secure_filename
import boto3
import os
import cv2
import json

from ..ai_model.model_label import inputdata
from . import food


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

            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)  # 파일 경로에서 직접 이미지를 읽습니다
            if img is None:
                return jsonify({"error": "Failed to read the image"}), 400

            # 이미지 처리 함수를 호출합니다
            confidence, label = inputdata(img)  # 수정된 inputdata 함수 호출

            with open('./app/foodnames.json', 'r', encoding='utf-8') as file:
                food_names = json.load(file)

            food_name = list(food_names.values())[label]


            return jsonify({"filename": filename, "confidence": confidence, "label": label, "food_name": food_name})
            
            # 이미지 읽기 및 전처리
            # image = Image.open(file_path).convert('RGB')
            # img_tensor = transform(image).unsqueeze(0)  # 모델 입력을 위한 텐서로 변환
            
            # with torch.no_grad():
            #         start = time.time()
            #         outputs = network(img_tensor)
            #         detection = outputs[0]  # 모델 출력이 튜플일 경우 첫 번째 요소 사용
            #         end = time.time()
            
            # print(f"YOLO v3 took {end - start:.5f} seconds")
            # max_value, max_index = torch.max(detection, dim=1)
            # print("가장 큰 값:", max_value)
            # print("가장 큰 값의 인덱스:", max_index)

            # # 결과 처리
            # class_names = []
            # boxes = []
            # scores = []

            # for i in range(detection.size(1)):
            #     if detection[0, i, 4] > probability_minimum:
            #         box = detection[0, i, :4]
            #         score = detection[0, i, 4]
            #         max_confidence_index = torch.argmax(detection[:, 4]).item()
            #         class_id = torch.argmax(detection[max_confidence_index, 5:]).item()

            #         print(class_id)
            #         class_name = labels[class_id]
                    
            #         boxes.append(box.tolist())
            #         scores.append(score.item())
            #         class_names.append(class_name)

            # # Draw boxes and labels on the image
            # image_np = np.array(image)
            # for box, score, class_name in zip(boxes, scores, class_names):
            #     x1, y1, x2, y2 = box
            #     cv2.rectangle(image_np, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            #     cv2.putText(image_np, f'{class_name}: {score:.2f}', (int(x1), int(y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

            # output_file_path = './app/static/images/output/' + filename
            # cv2.imwrite(output_file_path, image_np)

    #         return render_template('home/weights2.html', products=class_names, user_image='images/output/' + filename)

    # return render_template('upload_form.html')