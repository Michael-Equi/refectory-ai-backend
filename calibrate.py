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
                break

    """
    Set the section boundaries 
    """

    print("Please select the boundaries")

    clicks = []
    cv2.setMouseCallback('frame', get_mouse_cb(clicks))

    section1, section2, section3 = None, None, None
    while not section3:
        if len(clicks) == 4:
            if not section1:
                section1 = clicks[:]
                frame = cv2.polylines(frame, np.int32([section1]), isClosed=True, color=(0, 0, 255),
                                      thickness=4)
            elif not section2:
                section2 = clicks[:]
                frame = cv2.polylines(frame, np.int32([section2]), isClosed=True, color=(0, 255, 0),
                                      thickness=4)
            elif not section3:
                section3 = clicks[:]
                frame = cv2.polylines(frame, np.int32([section3]), isClosed=True, color=(255, 0, 0),
                                      thickness=4)
            clicks.clear()
            cv2.imshow('frame', frame)
        cv2.waitKey(1)

    """
    Output the calibration    
    """
    calib = Calibration(section1=section1,
                        section2=section2,
                        section3=section3,
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
