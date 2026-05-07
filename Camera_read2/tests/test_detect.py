import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import cv2
from detect import detect_bright_regions


DEFAULT_CONFIG = {
    "detection": {
        "brightness_threshold": 200,
        "blur_kernel": 11,
        "morph_kernel": 5,
        "min_roi_area": 500,
        "max_roi_area": 50000,
        "max_aspect_ratio": 5.0,
        "padding": 10,
        "max_regions": 10
    }
}


def _make_frame_with_bright_spot(x, y, radius, brightness=255):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.circle(frame, (x, y), radius, (brightness, brightness, brightness), -1)
    return frame


def test_detects_single_bright_spot():
    frame = _make_frame_with_bright_spot(320, 240, 30)
    regions = detect_bright_regions(frame, DEFAULT_CONFIG)
    assert len(regions) == 1
    bbox = regions[0]["bbox"]
    # Center of detected region should be near the bright spot
    cx, cy = regions[0]["center"]
    assert abs(cx - 320) < 50
    assert abs(cy - 240) < 50


def test_detects_multiple_spots():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.circle(frame, (100, 240), 25, (255, 255, 255), -1)
    cv2.circle(frame, (500, 240), 25, (255, 255, 255), -1)
    regions = detect_bright_regions(frame, DEFAULT_CONFIG)
    assert len(regions) == 2
    # Should be sorted left to right
    assert regions[0]["bbox"][0] < regions[1]["bbox"][0]


def test_ignores_dim_areas():
    # Spot with brightness below threshold should not be detected
    frame = _make_frame_with_bright_spot(320, 240, 30, brightness=100)
    regions = detect_bright_regions(frame, DEFAULT_CONFIG)
    assert len(regions) == 0


def test_ignores_tiny_spots():
    # Very small spot below min_roi_area
    frame = _make_frame_with_bright_spot(320, 240, 3)
    regions = detect_bright_regions(frame, DEFAULT_CONFIG)
    assert len(regions) == 0


def test_respects_max_regions():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    for i in range(5):
        cv2.circle(frame, (80 + i * 120, 240), 25, (255, 255, 255), -1)
    config = dict(DEFAULT_CONFIG)
    config["detection"] = dict(config["detection"])
    config["detection"]["max_regions"] = 2
    regions = detect_bright_regions(frame, config)
    assert len(regions) <= 2


def test_empty_frame_returns_no_regions():
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    regions = detect_bright_regions(frame, DEFAULT_CONFIG)
    assert len(regions) == 0


def test_region_has_expected_keys():
    frame = _make_frame_with_bright_spot(320, 240, 30)
    regions = detect_bright_regions(frame, DEFAULT_CONFIG)
    assert len(regions) == 1
    region = regions[0]
    assert "bbox" in region
    assert "area" in region
    assert "center" in region
    assert len(region["bbox"]) == 4
