from flask import Flask, send_file, request, jsonify
import cv2
import math


app = Flask(__name__)

cap = cv2.VideoCapture(0)


def get_frame():
    ret, frame = cap.read()
    if ret:
        return frame
    else:
        Exception("Problem getting frame from camera")


def generate_crops_from_annotations():
    pass


def draw_annotations(annotations, image):
    section = 1
    color = (0, 0, 255)
    if section == 1:
        color = (0, 255, 0)
    elif section == 2:
        color = (255, 0, 0)

    for annotation in annotations:
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


@app.route('/api/image', methods=['GET'])
def get_image():
    annotations.clear()
    frame = get_frame()
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


@app.route('/api/push', methods=['POST'])
def push():
    return jsonify({"success": False})
    # add in the annotation
    # return send_file(tmp_annotated_img_location, mimetype='image/png')
