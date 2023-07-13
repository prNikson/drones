import cv2
from djitellopy import Tello
from ultralytics import YOLO

model = YOLO("yolov8n.pt")


drone = Tello()
drone.connect()

# 627e03
def main():
    drone.streamon()
    print(drone.get_battery())
    while True:
        frame = drone.get_frame_read().frame

#        detected_frame = detect_objects(frame)
        res = model.predict(source=frame, show=True)
        cv2.imshow("Drone Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    drone.streamoff()
    drone.disconnect()
    cv2.destroyAllWindows()


# def detect_objects(frame):
#
#     return frame


if __name__ == "__main__":
    main()

