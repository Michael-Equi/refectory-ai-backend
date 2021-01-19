from flask import Flask, send_file, request
import cv2
import time

app = Flask(__name__)


@app.route('/time')
def get_current_time():
    return {'time': time.time()}


@app.route('/image')
def get_image():
    return send_file('/Users/michaelequi/Desktop/Screen Shot 2020-12-26 at 4.34.44 PM.png', mimetype='image/png')


@app.route('/addAnnotation', methods=['POST'])
def add_annotation():
    if request.method == 'POST':
        img = cv2.imread('/Users/michaelequi/Desktop/Screen Shot 2021-01-16 at 12.29.10 AM.png')
        cv2.write('newimage.png', img)
        print(request.json)
        return send_file('newimage.png', mimetype='image/png')
