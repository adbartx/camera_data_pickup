import cv2
import numpy as np


def extract_roi(frame, bbox) -> np.ndarray:
    x1, y1, x2, y2 = bbox
    return frame[y1:y2, x1:x2]


def extract_hsv_features(roi_image) -> list:
    hsv = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    return [
        float(np.mean(h)), float(np.mean(s)), float(np.mean(v)),
        float(np.std(h)), float(np.std(s)), float(np.std(v))
    ]
