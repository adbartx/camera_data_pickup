import json
import cv2
from capture import Camera
from detect import detect_bright_regions, draw_regions

ZONE_DEFAULTS = {
    "display": {
        "labels": ["red", "yellow", "green"],
        "status_map": {"red": "error", "yellow": "warning", "green": "ok"},
        "model_path": "models/display_knn.joblib"
    },
    "diode": {
        "labels": ["red", "green"],
        "status_map": {"red": "error", "green": "ok"},
        "model_path": "models/diode_knn.joblib"
    }
}


def _next_zone_name(zones, zone_type):
    existing = [k for k in zones if k.startswith(zone_type + "_") or k == zone_type]
    if not existing:
        return f"{zone_type}_1"
    nums = []
    for k in existing:
        parts = k.split("_")
        if len(parts) >= 2 and parts[-1].isdigit():
            nums.append(int(parts[-1]))
    next_num = max(nums, default=0) + 1
    return f"{zone_type}_{next_num}"


def calibrate(config):
    cam_cfg = config["camera"]
    zones = {}

    with Camera(cam_cfg["device_index"], cam_cfg["resolution"]) as cam:
        print("Calibration — camera is open")
        print("Press SPACE to capture and detect, 'q' to finish\n")

        while True:
            try:
                frame = cam.read()
            except RuntimeError:
                print("\nCamera disconnected, saving what we have...")
                break
            cv2.imshow("Calibration", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
            if key != ord(" "):
                continue

            # Capture and detect
            regions = detect_bright_regions(frame, config)
            if not regions:
                print("No bright regions detected. Adjust lighting or detection settings.")
                continue

            # Show detected regions
            display = draw_regions(frame, regions)
            cv2.imshow("Calibration", display)
            cv2.waitKey(100)

            print(f"\nDetected {len(regions)} regions:")
            for i, region in enumerate(regions):
                print(f"  [{i + 1}] bbox={region['bbox']}, area={region['area']}")

            # Assign each region to a zone
            for i, region in enumerate(regions):
                while True:
                    choice = input(f"\nRegion {i + 1} — assign to zone (display/diode/skip): ").strip().lower()
                    if choice in ("display", "diode", "skip"):
                        break
                    print("Invalid choice. Enter 'display', 'diode', or 'skip'.")

                if choice == "skip":
                    continue

                zone_name = _next_zone_name(zones, choice)

                if choice in ZONE_DEFAULTS:
                    zone_data = dict(ZONE_DEFAULTS[choice])
                else:
                    zone_data = {"labels": [], "status_map": {}, "model_path": f"models/{choice}_knn.joblib"}

                zone_data["roi"] = region["bbox"]
                zone_data["model_path"] = f"models/{zone_name}_knn.joblib"
                zones[zone_name] = zone_data
                print(f"  -> Region {i + 1} assigned to '{zone_name}'")

            print(f"\nAssigned zones: {list(zones.keys())}")
            print("Press SPACE to re-detect, 'q' to save and finish")

    cv2.destroyAllWindows()
    return zones


def save_calibration(config, zones, config_path="config.json"):
    config["zones"] = zones
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\nCalibration saved to {config_path}")
    for name, zone in zones.items():
        print(f"  {name}: roi={zone['roi']}, labels={zone['labels']}")


if __name__ == "__main__":
    try:
        with open("config.json") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config.json: {e}")
        raise SystemExit(1)

    zones = calibrate(config)
    if zones:
        save_calibration(config, zones)
    else:
        print("No zones assigned. Config not modified.")
