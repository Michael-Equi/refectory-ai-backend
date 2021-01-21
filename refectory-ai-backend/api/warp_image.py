import cv2
import numpy as np
import models


def warp_image(points, img, tag_size=100):
    pts1 = np.float32([points[3], points[2], points[1], points[0]])  # [top left, top right, bottom left, bottom right]
    # [top left, top right, bottom left, bottom right]
    pts2 = np.float32([[0, tag_size], [0, 0], [tag_size, 0], [tag_size, tag_size]])
    h = cv2.getPerspectiveTransform(pts1, pts2)

    """
    Determine the range of the transformation on a restricted domain
    """
    min_x, min_y, max_x, max_y = 0, 0, 0, 0

    def consider_point(x):
        nonlocal min_x, min_y, max_x, max_y
        b = np.dot(h, x)
        b /= b[2]
        if b[0] > max_x:
            max_x = b[0]
        elif b[0] < min_x:
            min_x = b[0]
        if b[1] > max_y:
            max_y = b[1]
        elif b[1] < min_y:
            min_y = b[1]

    # handle left edge
    for i in range(img.shape[0]):
        x = np.float32([0, i, 1])
        consider_point(x)

    # handle right edge
    for i in range(img.shape[0]):
        x = np.float32([img.shape[1], i, 1])
        consider_point(x)

    # handle top edge
    for i in range(img.shape[1]):
        x = np.float32([i, 0, 1])
        consider_point(x)

    # handle bottom edge
    for i in range(img.shape[1]):
        x = np.float32([i, img.shape[0], 1])
        consider_point(x)

    # restrict between -3000, -3000, 3000, 3000
    min_x, min_y, max_x, max_y = max(min_x, -3000), max(min_y, -3000), min(max_x, 3000), min(max_y, 3000)

    # translating the image so that it appears entirely in the positive region of the matrix
    h_t = np.float32([[1, 0, -min_x],
                      [0, 1, -min_y],
                      [0, 0, 1]])
    dst = cv2.warpPerspective(img, np.dot(h_t, h), (int(-min_x + max_x), int(-min_y + max_y)))
    return dst, np.dot(h_t, h), int(-min_x + max_x), int(-min_y + max_y)


def warp_with_calibration(img, calibration):
    img = cv2.warpPerspective(img, np.float32(calibration.homography),
                              (calibration.homography_x, calibration.homography_y))
    # Return image with roi
    img = img[calibration.roi_top_left[1]:calibration.roi_bottom_right[1],
              calibration.roi_top_left[0]:calibration.roi_bottom_right[0]]
    return img
