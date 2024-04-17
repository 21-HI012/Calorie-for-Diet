from flask import render_template, request, Response
import os
import cv2
import numpy as np
import time
import json
import time
from datetime import datetime
from flask_login import current_user
from .models import Food
from ..record.models import Record
from ..user.routes import record as day_record
from ..extension import db
from . import food

configuration_path = "./cfg/yolov3.cfg"
weights_path = "./yolov3.weights"

labels = open("./data/coco.names").read().strip().split('\n')

probability_minimum = 0.5
threshold = 0.3
network = cv2.dnn.readNetFromDarknet(configuration_path, weights_path)

layers_names_all = network.getLayerNames()
layers_indexes_output = network.getUnconnectedOutLayers().flatten()
layers_names_output = [layers_names_all[i - 1] for i in layers_indexes_output]

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@food.route('/food_record')
def food_record():
    with open('./static/nutrition.json') as f:
        nutrition_data = json.load(f)

    new_record = Record(user_id=current_user.id, date=datetime.now(), image=filename)
    db.session.add(new_record)
    db.session.commit()
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
                t_record.t_calories += i['calories']
                t_record.t_sodium += i['sodium']
                t_record.t_carbohydrate += i['carbohydrate']
                t_record.t_fat += i['fat']
                t_record.t_cholesterol += i['cholesterol']
                t_record.t_protein += i['protein']
                db.session.commit()
        
    return Response(day_record())


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


@food.route("/result_cam", methods = ['GET','POST'])
def result_cam():
    global food_weight
    if request.method == 'POST':
        food_weight = []
        for food in products:
            weight = request.form.get(food)
            food_weight.append(weight)
        print(food_weight)
    return render_template('home/cam_predict.html', products=products, user_image='images/output/' + filename, food_weight=food_weight)


@food.route("/predict", methods = ['GET','POST'])
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


@food.route("/cam_predict/<img_name>")
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