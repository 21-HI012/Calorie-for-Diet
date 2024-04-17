from flask import render_template, Response
import cv2
import pyzbar.pyzbar as pyzbar
from ..extension import socketio
from . import barcode

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


@barcode.route('/video_feed')
def video_feed():
    return Response(scan_barcode(), mimetype='multipart/x-mixed-replace; boundary=frame')


@barcode.route('/barcode')
def barcode():
    return render_template('home/barcode.html')
