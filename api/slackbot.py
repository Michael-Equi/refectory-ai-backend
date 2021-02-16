import cv2
import numpy as np
from slack import WebClient
import uuid
import os


def generate_image_attachment_from_url(url):
    # post = '[{' + f'"text": "hgfhgf", "image_url": {url}' + '}]'
    post = '[{"text": "", "image_url": "' + url + '"}]'
    return post


def add_sub_image(origin, image, sub_image, text):
    # origin = (height, width)
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 1)[0]
    height, width, _ = sub_image.shape
    image[origin[0] + text_size[1]//2:origin[0] + text_size[1]//2 + height, origin[1]:origin[1] + width] = sub_image
    image = cv2.putText(image, text,
                        (origin[1] + width // 2 - text_size[0] // 2, origin[0]),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
    return image


def generate_image(dishes):
    assert len(dishes) > 0

    # Get dimensions for constructing the properly sized image
    text_size = cv2.getTextSize('Refectory AI', cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    upper_text_space = text_size[1] + 50
    space_btw_sub_images = 50
    sub_image_shape = dishes[0]['image'].shape

    width = 640
    height = upper_text_space + (1 + len(dishes)) // 2 * (sub_image_shape[0] + 2 * space_btw_sub_images)

    # Construct the image
    blank_image = np.full((height, width, 3), 255, np.uint8)
    image = cv2.putText(blank_image, 'Refectory AI',
                        (width // 2 - text_size[0] // 2, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 0), 2,
                        cv2.LINE_AA)

    # Add in sub images
    for i, dish in enumerate(dishes):
        assert dish['image'].shape == sub_image_shape
        w = round(3 / 4 * width) - sub_image_shape[1] // 2 if i % 2 else round(1 / 4 * width) - sub_image_shape[1] // 2
        h = (upper_text_space + space_btw_sub_images) + (sub_image_shape[0] + space_btw_sub_images) * (i // 2)
        image = add_sub_image((h, w), image, dish['image'], dish['meta'].name)

    return image


class RefectoryAISlack:
    def __init__(self):
        self.token = "xoxb-1755057314643-1740086766167-cJxvnwSlKz1UwiU0jXvRQDDI"
        self.client = WebClient(token=self.token)

    def post(self, url):
        attachment = generate_image_attachment_from_url(url)
        response = self.client.chat_postMessage(channel='#refectory',
                                                text="Today's Meal",
                                                attachments=attachment)
        if response['ok']:
            return True
        else:
            return False
