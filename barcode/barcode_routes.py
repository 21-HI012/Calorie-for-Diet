from flask import render_template, Response
import requests
import cv2
import pyzbar.pyzbar as pyzbar
from ..extension import socketio
from . import barcode

def scan_barcode():
    cap = cv2.VideoCapture(0)
    cap.set(3, 320)
    cap.set(4, 240)

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            for code in pyzbar.decode(frame):
                my_code = code.data.decode('utf-8')
                if my_code:
                    get_and_save_food_info(my_code)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            byte_image = buffer.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + byte_image + b'\r\n')
    
    finally:
        cap.release()
        cv2.destroyAllWindows()


@barcode.route('/video_feed')
def video_feed():
    return Response(scan_barcode(), mimetype='multipart/x-mixed-replace; boundary=frame')


def get_and_save_food_info(my_code):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        "Content-Type": "application/json"
    }

    food_response = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{my_code}", headers=headers)
    food_response.raise_for_status()
    food_data = food_response.json()

    if food_data['status'] == 1:
        product = food_data['product']

        # 무게 정보 처리
        weight = product.get('quantity')
        if weight:
            weight = int(weight.split(' ')[0])
        else:
            weight = None

        food_info = {
            "barcode": my_code,
            "name": product.get('product_name'),
            "weight": weight,
            "calories": product.get('nutriments', {}).get('energy-kcal', 0),
            "sodium": product.get('nutriments', {}).get('sodium', 0),
            "carbohydrate": product.get('nutriments', {}).get('carbohydrates', 0),
            "fat": product.get('nutriments', {}).get('fat', 0),
            "cholesterol": product.get('nutriments', {}).get('cholesterol', 0),
            "protein": product.get('nutriments', {}).get('proteins', 0)
        }

        socketio.emit('barcode', {'food_info': food_info})

    else:
        socketio.emit('no_match_data')


@barcode.route('/barcode')
def barcode():
    return render_template('barcode/barcode.html')
