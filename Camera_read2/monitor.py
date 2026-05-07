import os
import time
from capture import Camera
from detect import detect_bright_regions
from features import extract_roi, extract_hsv_features
from classifier import load_model, predict
from output import log_event


class ColorMonitor:
    def __init__(self, config):
        self.config = config
        self.models = {}
        self.prev_colors = {}
        self.last_heartbeat = {}

        # Load trained models for each zone
        for name, zone in config["zones"].items():
            model_path = zone["model_path"]
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"Model for zone '{name}' not found at '{model_path}'. "
                    f"Run: python3 train.py train --zone {name}"
                )
            self.models[name] = load_model(model_path)
            self.prev_colors[name] = None
            self.last_heartbeat[name] = 0

    def _match_dynamic_roi(self, regions, zone_name):
        zone = self.config["zones"][zone_name]
        saved_bbox = zone["roi"]
        saved_cx = (saved_bbox[0] + saved_bbox[2]) // 2
        saved_cy = (saved_bbox[1] + saved_bbox[3]) // 2

        best = None
        best_dist = float("inf")
        for region in regions:
            cx, cy = region["center"]
            dist = ((cx - saved_cx) ** 2 + (cy - saved_cy) ** 2) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best = region

        # Only accept if reasonably close to calibrated position
        max_drift = max(saved_bbox[2] - saved_bbox[0], saved_bbox[3] - saved_bbox[1]) * 2
        if best and best_dist <= max_drift:
            return best["bbox"]
        return None

    def process_frame(self, frame):
        mode = self.config["monitoring"]["detection_mode"]
        heartbeat_interval = self.config["monitoring"]["log_heartbeat_seconds"]
        log_all = self.config["monitoring"]["log_all_readings"]
        now = time.time()

        regions = None
        if mode == "dynamic":
            regions = detect_bright_regions(frame, self.config)

        for name, zone in self.config["zones"].items():
            # Get ROI bbox
            if mode == "dynamic" and regions is not None:
                bbox = self._match_dynamic_roi(regions, name)
                if bbox is None:
                    log_event(name, "unknown", "warning", event_type="roi_lost")
                    continue
            else:
                bbox = zone["roi"]

            # Extract features and classify
            roi_image = extract_roi(frame, bbox)
            if roi_image.size == 0:
                continue

            features = extract_hsv_features(roi_image)
            color = predict(self.models[name], features)
            status = zone["status_map"].get(color, "unknown")

            prev = self.prev_colors[name]
            changed = color != prev

            # Log on change, heartbeat, or if log_all is enabled
            should_log = changed or log_all
            if not should_log and heartbeat_interval > 0:
                if now - self.last_heartbeat.get(name, 0) >= heartbeat_interval:
                    should_log = True

            if should_log:
                event_type = "change" if changed else "heartbeat" if not log_all else "reading"
                log_event(name, color, status, prev_color=prev, event_type=event_type, features=features)
                self.last_heartbeat[name] = now

            self.prev_colors[name] = color

    def run(self):
        cam_cfg = self.config["camera"]
        interval = self.config["monitoring"]["interval_seconds"]
        max_errors = 5

        print("Starting color monitor (Ctrl+C to stop)")
        with Camera(cam_cfg["device_index"], cam_cfg["resolution"]) as cam:
            consecutive_errors = 0
            while True:
                try:
                    frame = cam.read()
                    self.process_frame(frame)
                    consecutive_errors = 0
                except RuntimeError as e:
                    consecutive_errors += 1
                    log_event("system", "error", "error",
                              event_type="camera_error",
                              features=None)
                    print(f"Camera error ({consecutive_errors}/{max_errors}): {e}",
                          flush=True)
                    if consecutive_errors >= max_errors:
                        raise RuntimeError(
                            f"Camera failed {max_errors}x in a row, stopping monitor"
                        )
                time.sleep(interval)
