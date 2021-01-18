import cv2
import numpy as np
from pupil_apriltags import Detector
import warp_image
import argparse


def main(args):
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
            if len(measurements) > args.num_samples:
                m = np.array(measurements)
                avg = np.average(m, axis=0)
                dst = warp_image.warp_image(avg, frame, tag_size=args.tag_size)
                cv2.imshow('video', dst)
                cv2.waitKey(1)
                break

    print("Please select the boundaries")
    bounds = []
    while len(bounds) < 4:
        pass
    camera.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calibrate refectory.ai')
    parser.add_argument('--tag-size', default=100, help='Size in pixels of the tag after calibration')
    parser.add_argument('--num-samples', default=5, help='Number of samples to take before averaging')
    args = parser.parse_args()
    main(args)
