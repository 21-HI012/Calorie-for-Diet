from flask import render_template, Response, request
import cv2
import datetime
import os
from . import cam

# def gen_frames():
#     camera = cv2.VideoCapture(1)
#     global frame
    
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame1 = buffer.tobytes()

#             yield (b'--frame\r\n'
#                 b'Content-Type: image/jpeg\r\n\r\n' + frame1 + b'\r\n')


# def result_code(my_code):
#     print(my_code)
#     return render_template('home/main.html')


# @cam.route('/video_feed')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@cam.route('/camera')
def camera():
    return render_template('home/cam.html')


@cam.route('/requests',methods=['POST','GET'])
def tasks():
    global path
    
    if request.method == 'POST':
        if request.form.get('capture'):
            now = datetime.datetime.now()
            img_name = "shot_{}.jpg".format(str(now).replace(":",''))
            print(img_name)
            path = os.path.sep.join(['static/shots', img_name])
            cv2.imwrite(p, frame)

    return render_template('home/cam_image.html', image_path=path[7:].replace("\\", "/"), img_name=img_name)


@cam.route('/retry')
def retry():
    os.remove(path)
    return render_template('home/cam.html')

