import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from features import extract_roi, extract_hsv_features


def test_extract_roi_returns_correct_subarray():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[10:20, 30:50] = 255
    roi = extract_roi(frame, [30, 10, 50, 20])
    assert roi.shape == (10, 20, 3)
    assert np.all(roi == 255)


def test_extract_roi_does_not_modify_frame():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    original = frame.copy()
    extract_roi(frame, [10, 10, 50, 50])
    assert np.array_equal(frame, original)


def test_extract_hsv_features_returns_6_values():
    # Create a solid red BGR image
    roi = np.zeros((20, 20, 3), dtype=np.uint8)
    roi[:, :] = [0, 0, 255]  # BGR red
    features = extract_hsv_features(roi)
    assert len(features) == 6
    assert all(isinstance(v, float) for v in features)


def test_extract_hsv_features_solid_color_has_zero_std():
    # Solid color -> std dev should be 0
    roi = np.full((20, 20, 3), [0, 255, 0], dtype=np.uint8)  # BGR green
    features = extract_hsv_features(roi)
    h_std, s_std, v_std = features[3], features[4], features[5]
    assert h_std == 0.0
    assert s_std == 0.0
    assert v_std == 0.0


def test_extract_hsv_features_different_colors_differ():
    red = np.full((20, 20, 3), [0, 0, 255], dtype=np.uint8)
    green = np.full((20, 20, 3), [0, 255, 0], dtype=np.uint8)
    red_features = extract_hsv_features(red)
    green_features = extract_hsv_features(green)
    # H mean should differ between red and green
    assert red_features[0] != green_features[0]
