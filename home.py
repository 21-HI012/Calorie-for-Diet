from flask import Flask, render_template, request, jsonify, Blueprint, Response
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from numpy import rec
from pyzbar.pyzbar import decode
import pyzbar.pyzbar as pyzbar
import json
import time
from datetime import datetime, date
from datetime import timedelta
from flask_login import current_user
from .user import *
from . import socketio

from .models import *
# from . import db
from sqlalchemy import cast, DATE
from sqlalchemy.sql import func

# from pymongo import MongoClient

# client = MongoClient('localhost', 27017)
# db = client.hanium

home = Blueprint('home', __name__)

configuration_path = "./cfg/yolov3.cfg"
weights_path = "./yolov3.weights"

labels = open("./data/coco.names").read().strip().split('\n')

# Setting minimum probability to eliminate weak predictions
probability_minimum = 0.5

# Setting threshold for non maximum suppression
threshold = 0.3
network = cv2.dnn.readNetFromDarknet(configuration_path, weights_path)

layers_names_all = network.getLayerNames()
# NumPy 배열을 반환하는 경우 (예: OpenCV 4.x 이상), flatten() 사용
layers_indexes_output = network.getUnconnectedOutLayers().flatten()
layers_names_output = [layers_names_all[i - 1] for i in layers_indexes_output]

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def html(content):
   return '<html><head></head><body>' + content + '</body></html>'


# 상세 기록 정보
@home.route('/food_record')
def food_record():
    with open('./static/nutrition.json') as f:
        nutrition_data = json.load(f)
        # print(json.dumps(nutrition_data))

    new_record = Record(user_id=current_user.id, date=datetime.now(), image=filename)
    db.session.add(new_record)
    db.session.commit()
    print(food_weight)
    for index, food in enumerate(products):
        for i in nutrition_data['nutrition']:
            if i['name'] == food:
                new_food = Food(record_id=new_record.id,
                                name=i['name'],
                                weight=food_weight[index],
                                calories=i['calories']*int(food_weight[index])/100, 
                                sodium=i['sodium']*int(food_weight[index])/100, 
                                carbohydrate=i['carbohydrate']*int(food_weight[index])/100, 
                                fat=i['fat']*int(food_weight[index])/100, 
                                cholesterol=i['cholesterol']*int(food_weight[index])/100,
                                protein=i['protein']*int(food_weight[index])/100)

                db.session.add(new_food)
                db.session.commit()
                
                t_record = Record.query.order_by(Record.id.desc()).first()
                print(t_record.t_calories)
                t_record.t_calories += i['calories']
                t_record.t_sodium += i['sodium']
                t_record.t_carbohydrate += i['carbohydrate']
                t_record.t_fat += i['fat']
                t_record.t_cholesterol += i['cholesterol']
                t_record.t_protein += i['protein']
                db.session.commit()

                # t_date = datetime.today().date()
                # food = Record.query.get(Record.user_id==current_user.id, Record.date>=t_date)
                # food.t_calories += i['calories']
                # db.session.commit()



    # food_list = Food.query.filter_by(record_id=new_record.id).all()
    
    # {'calories': 74.0, 'sodium': 102.0, 'carbohydrate': 17.0, 'fat': 0.4, 'cholesterol': 0.0, 'protein': 3.6999999999999997}

    # return render_template('user/record.html', date = date)
    return Response(record())


def scan_barcode():
    cap = cv2.VideoCapture(0)
    cap.set(3, 320)
    cap.set(4, 240)

    while True:
        success, frame = cap.read()
        if not success:
            break

        for code in pyzbar.decode(frame):
            my_code = code.data.decode('utf-8')
            if my_code:
                cap.release()
                cv2.destroyAllWindows()
                socketio.emit('barcode', {'code': my_code})
        
        ret, buffer = cv2.imencode('.jpg', frame)
        byte_image = buffer.tobytes()

        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + byte_image + b'\r\n')


@home.route('/video_feed')
def video_feed():
    return Response(scan_barcode(), mimetype='multipart/x-mixed-replace; boundary=frame')


@home.route('/barcode')
def barcode():
    return render_template('home/barcode.html')


@home.route('/barcode_record/<my_code>')
def barcode_record(my_code):
    with open('./static/food.json') as f:
        food_data = json.load(f)

    new_record = Record(user_id=current_user.id, date=datetime.now())
    db.session.add(new_record)
    db.session.commit()
    for i in food_data['food']:
        if i['barcode'] == my_code:
            new_food = Food(record_id=new_record.id,
                            name=i['name'],
                            weight=i['weight'],
                            calories=i['calories'], 
                            sodium=i['sodium'], 
                            carbohydrate=i['carbohydrate'], 
                            fat=i['fat'], 
                            cholesterol=i['cholesterol'],
                            protein=i['protein'])

            db.session.add(new_food)
            db.session.commit()
            
            t_record = Record.query.order_by(Record.id.desc()).first()
            print(t_record.t_calories)
            t_record.t_calories += i['calories']
            t_record.t_sodium += i['sodium']
            t_record.t_carbohydrate += i['carbohydrate']
            t_record.t_fat += i['fat']
            t_record.t_cholesterol += i['cholesterol']
            t_record.t_protein += i['protein']
            db.session.commit()

    return Response(record())


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

    return render_template('home/main.html', t_nutrition=t_nutrition, t_date=t_date, 
                            per_nutrition=per_nutrition, sodium=t_nutrition['sodium'], carbohydrate=t_nutrition['carbohydrate'],
                            fat=t_nutrition['fat'], cholesterol=t_nutrition['cholesterol'], protein=t_nutrition['protein'])


# @home.route('/camera')
# def camera():
#     return render_template('home/camera.html')

@home.route("/upload", methods=['GET', 'POST'])
def upload():
    return render_template('home/upload.html')

@home.route("/result", methods = ['GET','POST'])
def result():
    global food_weight
    if request.method == 'POST':
        food_weight = []
        for food in products:
            weight = request.form.get(food)
            food_weight.append(weight)
        print(food_weight)
    return render_template('home/predict.html', products=products, user_image='images/output/' + filename, food_weight=food_weight)

@home.route("/result_cam", methods = ['GET','POST'])
def result_cam():
    global food_weight
    if request.method == 'POST':
        food_weight = []
        for food in products:
            weight = request.form.get(food)
            food_weight.append(weight)
        print(food_weight)
    return render_template('home/cam_predict.html', products=products, user_image='images/output/' + filename, food_weight=food_weight)

@home.route("/predict", methods = ['GET','POST'])
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
                print(file_path)
                pathImage = file_path
                image_input = img = cv2.imread(pathImage)
                image_input_shape = image_input.shape
      
                blob = cv2.dnn.blobFromImage(image_input, 1 / 255.0, (416, 416), swapRB=True, crop=False)
                # Slicing blob and transposing to make channels come at the end
                blob_to_show = blob[0, :, :, :].transpose(1, 2, 0)           
                
                network.setInput(blob)  # setting blob as input to the network
                start = time.time()
                output_from_network = network.forward(layers_names_output)
                end = time.time()
                
                # Showing spent time for forward pass
                print('YOLO v3 took {:.5f} seconds'.format(end - start))
                np.random.seed(42)
                # randint(low, high=None, size=None, dtype='l')
                colors = np.random.randint(0, 255, size=(len(labels), 3))
                
                bounding_boxes = []
                confidences = []
                class_numbers = []
                h, w = image_input_shape[:2]  # Slicing from tuple only first two elements
                
                for result in output_from_network:
                    # Going through all detections from current output layer
                    for detection in result:
                        # Getting class for current object
                        scores = detection[5:]
                        class_current = np.argmax(scores)
                        confidence_current = scores[class_current]

                        if confidence_current > probability_minimum:    
                            box_current = detection[0:4] * np.array([w, h, w, h])
                            x_center, y_center, box_width, box_height = box_current.astype('int')
                            x_min = int(x_center - (box_width / 2))
                            y_min = int(y_center - (box_height / 2))
                
                            # Adding results into prepared lists
                            bounding_boxes.append([x_min, y_min, int(box_width), int(box_height)])
                            confidences.append(float(confidence_current))
                            class_numbers.append(class_current)
                results = cv2.dnn.NMSBoxes(bounding_boxes, confidences, probability_minimum, threshold)
            
                objects=[]
                for i in range(len(class_numbers)):
                    print(labels[int(class_numbers[i])])
                    for n in nutrition_data['nutrition']:
                        if n['name'] == labels[int(class_numbers[i])]:
                            objects.append(labels[int(class_numbers[i])])
                # Saving found labels
                """with open('found_labels.txt', 'w') as f:
                    for i in range(len(class_numbers)):
                        f.write(labels[int(class_numbers[i])])"""
                if len(results) > 0:
                    # Going through indexes of results
                    for i in results.flatten():
                        # Getting current bounding box coordinates
                        x_min, y_min = bounding_boxes[i][0], bounding_boxes[i][1]
                        box_width, box_height = bounding_boxes[i][2], bounding_boxes[i][3]
                
                        colour_box_current = [int(j) for j in colors[class_numbers[i]]]
                
                        cv2.rectangle(image_input, (x_min, y_min), (x_min + box_width, y_min + box_height),
                                        colour_box_current, 5)
                
                        
                        text_box_current = '{}: {:.4f}'.format(labels[int(class_numbers[i])], confidences[i])
                
                        cv2.putText(image_input, text_box_current, (x_min, y_min - 7), cv2.FONT_HERSHEY_SIMPLEX,
                                    1.5, colour_box_current, 5)   
                cv2.imwrite('./static/images/output/' + filename , image_input)

                products = list(set(objects))
                print(products)
                
                return render_template('home/weights2.html', products = list(set(objects)), user_image = 'images/output/' + filename)
                
        except Exception as e:
            return "Unable to read the file. Please check if the file extension is correct."

@home.route("/cam_predict/<img_name>")
def cam_predict(img_name):
    with open('./static/nutrition.json') as f:
        nutrition_data = json.load(f)

    global products, user_image, filename
    # if request.method == 'POST':
    #     file = request.files['file']
    try:
        filename = img_name
        file_path = os.path.join('./static/shots', filename)
        # file.save(file_path)
        print(file_path)
        pathImage = file_path
        image_input = img = cv2.imread(pathImage)
        image_input_shape = image_input.shape

        blob = cv2.dnn.blobFromImage(image_input, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        # Slicing blob and transposing to make channels come at the end
        blob_to_show = blob[0, :, :, :].transpose(1, 2, 0)           
        
        network.setInput(blob)  # setting blob as input to the network
        start = time.time()
        output_from_network = network.forward(layers_names_output)
        end = time.time()
        
        # Showing spent time for forward pass
        print('YOLO v3 took {:.5f} seconds'.format(end - start))
        np.random.seed(42)
        # randint(low, high=None, size=None, dtype='l')
        colors = np.random.randint(0, 255, size=(len(labels), 3))
        
        bounding_boxes = []
        confidences = []
        class_numbers = []
        h, w = image_input_shape[:2]  # Slicing from tuple only first two elements
        
        for result in output_from_network:
            # Going through all detections from current output layer
            for detection in result:
                # Getting class for current object
                scores = detection[5:]
                class_current = np.argmax(scores)
                confidence_current = scores[class_current]

                if confidence_current > probability_minimum:    
                    box_current = detection[0:4] * np.array([w, h, w, h])
                    x_center, y_center, box_width, box_height = box_current.astype('int')
                    x_min = int(x_center - (box_width / 2))
                    y_min = int(y_center - (box_height / 2))
        
                    # Adding results into prepared lists
                    bounding_boxes.append([x_min, y_min, int(box_width), int(box_height)])
                    confidences.append(float(confidence_current))
                    class_numbers.append(class_current)
        results = cv2.dnn.NMSBoxes(bounding_boxes, confidences, probability_minimum, threshold)
    
        objects=[]
        for i in range(len(class_numbers)):
            print(labels[int(class_numbers[i])])
            for n in nutrition_data['nutrition']:
                if n['name'] == labels[int(class_numbers[i])]:
                    objects.append(labels[int(class_numbers[i])])
        # Saving found labels
        """with open('found_labels.txt', 'w') as f:
            for i in range(len(class_numbers)):
                f.write(labels[int(class_numbers[i])])"""
        if len(results) > 0:
            # Going through indexes of results
            for i in results.flatten():
                # Getting current bounding box coordinates
                x_min, y_min = bounding_boxes[i][0], bounding_boxes[i][1]
                box_width, box_height = bounding_boxes[i][2], bounding_boxes[i][3]
        
                colour_box_current = [int(j) for j in colors[class_numbers[i]]]
        
                cv2.rectangle(image_input, (x_min, y_min), (x_min + box_width, y_min + box_height),
                                colour_box_current, 5)
        
                
                text_box_current = '{}: {:.4f}'.format(labels[int(class_numbers[i])], confidences[i])
        
                cv2.putText(image_input, text_box_current, (x_min, y_min - 7), cv2.FONT_HERSHEY_SIMPLEX,
                            1.5, colour_box_current, 5)   
        cv2.imwrite('./static/images/output/' + filename, image_input)

        products = list(set(objects))
        print(products)
            
        return render_template('home/weights_cam.html', products = list(set(objects)), user_image = 'images/output/' + filename)
            
    except Exception as e:
        return "Unable to read the file. Please check if the file extension is correct."