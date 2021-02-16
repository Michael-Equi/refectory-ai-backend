from flask import Flask, send_file, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, storage
import cv2
import os
import math
import uuid
import json
from datetime import date
import time

import models
import warp_image
import slackbot

app = Flask(__name__)

""" OpenCV """
cap = cv2.VideoCapture(1)

""" Firebase """
config = {
    "apiKey": "AIzaSyC2qvy80zegkDmLkJM18CSiSj_cz21PWZk",
    "authDomain": "refectory-ai.firebaseapp.com",
    "projectId": "refectory-ai",
    "storageBucket": "refectory-ai.appspot.com",
    "databaseURL": "https://databaseName.firebaseio.com",
    "messagingSenderId": "392671167282",
    "appId": "1:392671167282:web:2b6c38f02676e86de0cd2b",
    "measurementId": "G-S557B9S0FY"
}
cred = credentials.Certificate('./refectory-ai-firebase-adminsdk-stydr-1a035f2f33.json')
firebase_admin.initialize_app(cred, config)
# db = firestore.client()
# doc_ref = db.collection(u'streams').document(u'EN6JbCUDiSMii9gfQl17')

""" Slack """
slack_client = slackbot.RefectoryAISlack()


"""
Helper functions
"""


def get_frame():
    ret, frame = cap.read()
    if ret:
        return frame
    else:
        Exception("Problem getting frame from camera")


def draw_annotations(annotations, image):
    for annotation in annotations:

        # Figure out the color of the annotation based on the section
        color = (0, 0, 255)
        if annotation['section'] == 1:
            color = (0, 255, 0)
        elif annotation['section'] == 2:
            color = (255, 0, 0)

        # Draw the annotations
        if annotation['round']:
            center = ((annotation['points'][0][0] + annotation['points'][1][0]) / 2,
                      (annotation['points'][0][1] + annotation['points'][1][1]) / 2)
            radius = int(math.sqrt((center[0] - annotation['points'][1][0]) ** 2 +
                                   (center[1] - annotation['points'][1][1]) ** 2))
            image = cv2.circle(image, (int(center[0]), int(center[1])), radius, color, 2)
        else:
            image = cv2.rectangle(image, tuple(annotation['points'][0]), tuple(annotation['points'][1]), color, 2)

    return image


def update_annotated_image_file():
    unannotated_image = cv2.imread(TMP_IMG_LOCATION)
    annotated_image = draw_annotations(g_annotations, unannotated_image)
    cv2.imwrite(TMP_ANNOTATED_IMG_LOCATION, annotated_image)


def upload_image(image):
    file = f'image{uuid.uuid4()}.png'
    cv2.imwrite(os.path.join('/tmp', file), image)
    bucket = storage.bucket()
    blob = bucket.blob(file)
    blob.upload_from_filename(os.path.join('/tmp', file))
    blob.make_public()
    return blob.public_url


def generate_dishes_from_annotations(annotations):
    dishes = []
    image = cv2.imread(TMP_IMG_LOCATION)
    for i, annotation in enumerate(annotations):
        pts = annotation['points']
        pt1_0 = min(pts[0][0], pts[1][0])
        pt2_0 = max(pts[0][0], pts[1][0])
        pt1_1 = min(pts[0][1], pts[1][1])
        pt2_1 = max(pts[0][1], pts[1][1])
        crop = image[pt1_1:pt2_1, pt1_0:pt2_0]
        output = cv2.resize(crop, (200, 200))
        dish = models.Dish(contents=annotation['content'], name=annotation['name'], round=annotation['round'],
                           section=annotation['section'])
        dishes.append({'meta': dish, 'image': output})
    return dishes


"""
APP CODE START
"""

g_annotations = []
DATA_DIR = os.path.expanduser('~/refectory-data')
os.makedirs(DATA_DIR, exist_ok=True)
TMP_IMG_LOCATION = '/tmp/refectory_image.png'
TMP_ANNOTATED_IMG_LOCATION = '/tmp/annotated_refectory_image.png'
CALIBRATION = models.Calibration.parse_file('config.json')


@app.route('/api/image', methods=['GET'])
def get_image():
    g_annotations.clear()
    frame = get_frame()
    frame = warp_image.warp_with_calibration(frame, CALIBRATION)
    cv2.imwrite(TMP_IMG_LOCATION, frame)
    return send_file(TMP_IMG_LOCATION, mimetype='image/png')


@app.route('/api/annotation', methods=['POST'])
def add_annotation():
    # add in the annotation
    g_annotations.append(request.get_json())
    update_annotated_image_file()
    return send_file(TMP_ANNOTATED_IMG_LOCATION, mimetype='image/png')


@app.route('/api/annotation/clear', methods=['POST'])
def clear_annotation():
    # clear all annotations but keep the same image
    g_annotations.clear()
    update_annotated_image_file()
    return send_file(TMP_ANNOTATED_IMG_LOCATION, mimetype='image/png')


@app.route('/api/annotation/undo', methods=['POST'])
def undo_annotation():
    # pop the last annotation
    g_annotations.pop()
    update_annotated_image_file()
    return send_file(TMP_ANNOTATED_IMG_LOCATION, mimetype='image/png')


@app.route('/api/section/clear', methods=['POST'])
def clear_section():
    pass


@app.route('/api/push', methods=['POST'])
def push():
    try:
        # Save image and annotation into a data directory
        today = date.today()
        data_name = today.strftime("%b-%d-%Y")
        data_time = str(int(time.time()))
        data_path = os.path.join(DATA_DIR, data_name)
        os.makedirs(data_path, exist_ok=True)
        with open(os.path.join(data_path, data_name + '_' + data_time + '.json'), 'w') as f:
            json.dump(g_annotations, f)
        cv2.imwrite(os.path.join(data_path, data_name + '_' + data_time + '.png'), cv2.imread(TMP_IMG_LOCATION))

        # Send the processed image to slack
        image = slackbot.generate_image(generate_dishes_from_annotations(g_annotations))
        url = upload_image(image)
        slack_client.post(url)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, 'exception': str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
