from flask import Flask, send_file, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, storage
import cv2
import os
import math
import uuid

import models
import warp_image

app = Flask(__name__)

cap = cv2.VideoCapture(0)

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
db = firestore.client()
doc_ref = db.collection(u'streams').document(u'EN6JbCUDiSMii9gfQl17')


def get_frame():
    ret, frame = cap.read()
    if ret:
        return frame
    else:
        Exception("Problem getting frame from camera")


def upload_dish_image(index, image):
    # image should be 100x100
    file = f'image{index}_{uuid.uuid4()}.png'
    cv2.imwrite(os.path.join('/tmp', file), image)
    bucket = storage.bucket()
    blob = bucket.blob(file)
    blob.upload_from_filename(os.path.join('/tmp', file))
    blob.make_public()
    return blob.public_url


def generate_dishes_from_annotations(annotations):
    dishes = []
    image = cv2.imread(tmp_img_location)
    for i, annotation in enumerate(annotations):
        pts = annotation['points']
        crop = image[pts[0][1]:pts[1][1], pts[0][0]:pts[1][0]]
        output = cv2.resize(crop, (100, 100))
        url = upload_dish_image(i, output)
        dish = models.Dish(contents=annotation['content'], image=url, name=annotation['name'],
                           round=annotation['round'], section=annotation['section'])
        dishes.append(dish)
    return dishes


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
    unannotated_image = cv2.imread(tmp_img_location)
    annotated_image = draw_annotations(annotations, unannotated_image)
    cv2.imwrite(tmp_annotated_img_location, annotated_image)


image = None
annotations = []
tmp_img_location = '/tmp/refectory_image.png'
tmp_annotated_img_location = '/tmp/annotated_refectory_image.png'
calibration = models.Calibration.parse_file('config.json')


@app.route('/api/image', methods=['GET'])
def get_image():
    annotations.clear()
    frame = get_frame()
    frame = warp_image.warp_with_calibration(frame, calibration)
    cv2.imwrite(tmp_img_location, frame)
    return send_file(tmp_img_location, mimetype='image/png')


@app.route('/api/annotation', methods=['POST'])
def add_annotation():
    # add in the annotation
    annotations.append(request.get_json())
    update_annotated_image_file()
    return send_file(tmp_annotated_img_location, mimetype='image/png')


@app.route('/api/annotation/clear', methods=['POST'])
def clear_annotation():
    # clear all annotations but keep the same image
    annotations.clear()
    update_annotated_image_file()
    return send_file(tmp_annotated_img_location, mimetype='image/png')


@app.route('/api/annotation/undo', methods=['POST'])
def undo_annotation():
    # pop the last annotation
    annotations.pop()
    update_annotated_image_file()
    return send_file(tmp_annotated_img_location, mimetype='image/png')


def clear_dishes(doc_ref, section_name):
    current_dishes = doc_ref.get().to_dict()[section_name]
    if len(current_dishes) > 0:
        doc_ref.update({section_name: firestore.ArrayRemove(current_dishes)})


@app.route('/api/section/clear', methods=['POST'])
def clear_section():
    try:
        print(request.get_json())
        section = request.get_json()['section']
        if section == 1:
            clear_dishes(doc_ref, 'section1')
        elif section == 2:
            clear_dishes(doc_ref, 'section2')
        elif section == 3:
            clear_dishes(doc_ref, 'section3')
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, 'exception': e})


@app.route('/api/push', methods=['POST'])
def push():
    sections_cleared = {1: False, 2: False, 3: False}
    try:
        for dish in generate_dishes_from_annotations(annotations):
            if dish.section == 1:
                if not sections_cleared[1]:
                    clear_dishes(doc_ref, 'section1')
                    sections_cleared[1] = True
                doc_ref.update({u'section1': firestore.ArrayUnion([dish.dict()])})
            elif dish.section == 2:
                if not sections_cleared[2]:
                    clear_dishes(doc_ref, 'section2')
                    sections_cleared[2] = True
                doc_ref.update({u'section2': firestore.ArrayUnion([dish.dict()])})
            else:
                if not sections_cleared[3]:
                    clear_dishes(doc_ref, 'section3')
                    sections_cleared[3] = True
                doc_ref.update({u'section3': firestore.ArrayUnion([dish.dict()])})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, 'exception': e})
