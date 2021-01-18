import cv2
import numpy as np
from pupil_apriltags import Detector
import warp_image

def main():
    print("Starting video")
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
        if len(results) > 0:
            measurements.append(results[0].corners)
            if len(measurements) > 5:
                m = np.array(measurements)
                avg = np.average(m, axis=0)
                dst = warp_image.warp_image(avg, frame)

                if not ret:
                    print("failed to grab frame")
                    break
                cv2.imshow('video', dst)
                if cv2.waitKey(20) & 0xFF == ord('q'):
                    break
    camera.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
