import cv2


def main():
    print("Starting video")
    camera = cv2.VideoCapture(0)
    while True:
        ret, frame = camera.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow('video', frame)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break
    camera.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()