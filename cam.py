from flask import Flask, render_template, Response, Blueprint, request, jsonify
import cv2
import datetime, time
import os
from pyzbar.pyzbar import decode
import pyzbar.pyzbar as pyzbar
from itertools import takewhile

cam = Blueprint('cam', __name__)
 # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

def gen_frames():  # generate frame by frame from camera
    camera = cv2.VideoCapture(1) 
    global frame
    # my_code = 0
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        # print(type(frame))
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame1 = buffer.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame1 + b'\r\n')

            # for code in pyzbar.decode(frame):
            #     my_code = code.data.decode('utf-8')
            #     if my_code:
            #         print(my_code)
            #         camera.release()
            #         return
                    # yield None
                    # return render_template('home/main.html')
                
    # yield Response(result_code(my_code))
                    # frame1_return = 0 
  # concat frame one by one and show result
                   
                    # gen = gen_frames()
                    # next(gen_frames())


# def stream_template(template_name):                                                                                                                                                 
#     cam.update_template_context()                                                                                                                                                       
#     t = app.jinja_env.get_template(template_name)                                                                                                                                              
#     rv = t.stream()                                                                                                                                                                     
#     rv.disable_buffering()                                                                                                                                                                     
#     return rv                                                                                                                                                                                  

def result_code(my_code):
    print(my_code)
    return render_template('home/main.html')
    # yield render_template('home/cam.html', my_code=my_code)
    # return render_template('home/main.html')
#     with app.app_context():
#         template = render_template('home/barcode.html')
#         return template

    

@cam.route('/barcode1')
def barcode1(my_code):
    return render_template('home/test.html', my_code=my_code)            


@cam.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@cam.route('/camera')
def camera():
    """Video streaming home page."""
    return render_template('home/cam.html')

@cam.route('/requests',methods=['POST','GET'])
def tasks():
    global p
    if request.method == 'POST':
        if request.form.get('capture'):
            now = datetime.datetime.now()
            img_name = "shot_{}.jpg".format(str(now).replace(":",''))
            print(img_name)
            p = os.path.sep.join(['static/shots', img_name])
            cv2.imwrite(p, frame)

    return render_template('home/cam_image.html', image_path=p[7:].replace("\\", "/"), img_name=img_name)

@cam.route('/retry')
def retry():
    os.remove(p)
    return render_template('home/cam.html')
