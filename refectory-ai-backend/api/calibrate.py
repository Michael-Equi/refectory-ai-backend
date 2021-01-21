import cv2
import numpy as np
from pupil_apriltags import Detector
import warp_image
import argparse
from pathlib import Path

from models import Calibration


def get_mouse_cb(clicks):
    def mouse_cb(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            clicks.append([x, y])
            print(clicks)

    return mouse_cb


def main(params):

    """
    Get the image and compute the necessary warping
    """

    homography, homography_x, homography_y = None, None, None

    measurements = []
    camera = cv2.VideoCapture(0)
    at_detector = Detector(families='tagStandard41h12',
                           nthreads=1,
                           quad_decimate=1.0,
                           quad_sigma=0.0,
                           refine_edges=1,
                           decode_sharpening=0.25,
                           debug=0)
    while True:
        ret, frame = camera.read()
        results = at_detector.detect(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        if not ret:
            print("failed to grab frame")
            break

        if len(results) > 0:
            measurements.append(results[0].corners)
            if len(measurements) > params.num_samples:
                m = np.array(measurements)
                avg = np.average(m, axis=0)
                frame, homography, homography_x, homography_y = warp_image.warp_image(avg, frame, tag_size=params.tag_size)
                cv2.imshow('frame', frame)
                cv2.waitKey(1)
                response = input("Enter 'y' to confirm calibration: ")
                if response == 'y':
                    break
                else:
                    measurements.clear()

    """
    Set ROI
    """

    print("Please select the boundaries (top left then bottom right)")

    clicks = []
    cv2.setMouseCallback('frame', get_mouse_cb(clicks))
    while True:
        if len(clicks) == 2:
            roi_frame = frame.copy()
            cv2.rectangle(roi_frame, tuple(clicks[0]), tuple(clicks[1]), (255, 255, 0), 2)
            cv2.imshow('frame', roi_frame)
            cv2.waitKey(1)
            response = input("Enter 'y' to confirm calibration: ")
            if response == 'y':
                break
            else:
                clicks.clear()
        cv2.waitKey(1)

    """
    Output the calibration
    """
    calib = Calibration(
        roi_top_left=clicks[0],
        roi_bottom_right=clicks[1],
        homography=homography.tolist(),
        homography_x=homography_x,
        homography_y=homography_y)

    print(calib.json())
    Path(params.config_path).write_text(calib.json())
    print(f"Calibration written to ${params.config_path}")

    # Cleanup
    camera.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calibrate refectory.ai')
    parser.add_argument('--tag-size', default=100, help='Size in pixels of the tag after calibration')
    parser.add_argument('--num-samples', default=5, help='Number of samples to take before averaging')
    parser.add_argument('--config-path', default='./config.json', help='Path for the config file to be written to')
    args = parser.parse_args()
    main(args)
