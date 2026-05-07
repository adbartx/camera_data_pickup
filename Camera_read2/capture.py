import cv2


class Camera:
    def __init__(self, device_index=1, resolution=(640, 480)):
        self.device_index = device_index
        self.resolution = resolution
        self.cap = None

    def __enter__(self):
        self.cap = cv2.VideoCapture(self.device_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera at index {self.device_index}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cap:
            self.cap.release()
        return False

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to read frame from camera")
        return frame


def preview(config):
    cam_cfg = config["camera"]
    with Camera(cam_cfg["device_index"], cam_cfg["resolution"]) as cam:
        print("Camera preview - press 'q' to quit")
        while True:
            frame = cam.read()
            cv2.imshow("Camera Preview", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    import json
    try:
        with open("config.json") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config.json: {e}")
        raise SystemExit(1)
    preview(config)
