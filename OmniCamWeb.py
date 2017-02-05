#!/usr/bin/env python
from flask import Flask, render_template, Response
import OmniCam as camera
import threading as thread

app = Flask(__name__)
cam = camera.Camera(0)

t = threading.Thread(target=cam.start_recording)
t.start()

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = cam.get_jpeg()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST' and request.form['username'] == 'admin' and request.form['passowrd'] == 'password':
        return render_template('camerapage.html')        

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
