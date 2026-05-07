import cv2
import numpy as np
from capture import Camera


def detect_bright_regions(frame, config) -> list:
    det = config["detection"]
    h, w = frame.shape[:2]

    # Convert to HSV, extract V (brightness) channel
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    v_channel = hsv[:, :, 2]

    # Blur to reduce noise
    kernel_size = det["blur_kernel"]
    blurred = cv2.GaussianBlur(v_channel, (kernel_size, kernel_size), 0)

    # Threshold to isolate bright areas
    _, binary = cv2.threshold(blurred, det["brightness_threshold"], 255, cv2.THRESH_BINARY)

    # Morphological cleanup — close gaps, then remove small noise
    morph_k = det["morph_kernel"]
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_k, morph_k))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)

    # Find contours
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    padding = det["padding"]
    min_area = det["min_roi_area"]
    max_area = det["max_roi_area"]
    max_ar = det["max_aspect_ratio"]

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area or area > max_area:
            continue

        x, y, bw, bh = cv2.boundingRect(contour)
        aspect_ratio = max(bw, bh) / max(min(bw, bh), 1)
        if aspect_ratio > max_ar:
            continue

        # Add padding, clamp to frame bounds
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(w, x + bw + padding)
        y2 = min(h, y + bh + padding)

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        regions.append({
            "bbox": [x1, y1, x2, y2],
            "area": int(area),
            "center": (cx, cy)
        })

    # Sort by x coordinate (left to right)
    regions.sort(key=lambda r: r["bbox"][0])

    # Limit number of regions
    return regions[:det["max_regions"]]


def draw_regions(frame, regions) -> np.ndarray:
    display = frame.copy()
    for i, region in enumerate(regions):
        x1, y1, x2, y2 = region["bbox"]
        cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(display, str(i + 1), (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return display


def preview_detection(config):
    cam_cfg = config["camera"]
    with Camera(cam_cfg["device_index"], cam_cfg["resolution"]) as cam:
        print("Detection preview - press 'q' to quit")
        while True:
            frame = cam.read()
            regions = detect_bright_regions(frame, config)
            display = draw_regions(frame, regions)

            info = f"Detected: {len(regions)} regions"
            cv2.putText(display, info, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Detection Preview", display)
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
    preview_detection(config)
