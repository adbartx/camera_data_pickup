import argparse
import csv
import json
import os
import cv2
import numpy as np
from capture import Camera
from features import extract_roi, extract_hsv_features
from classifier import train, evaluate, save_model


def collect_samples(config, zone_name):
    if zone_name not in config["zones"]:
        print(f"Zone '{zone_name}' not found in config. Run calibrate.py first.")
        return

    zone = config["zones"][zone_name]
    bbox = zone["roi"]
    labels = zone["labels"]

    # Build key-to-label mapping from first letter
    key_map = {}
    for label in labels:
        key = label[0].lower()
        key_map[key] = label

    csv_path = f"training_data/{zone_name}_samples.csv"
    os.makedirs("training_data", exist_ok=True)
    file_exists = os.path.exists(csv_path)

    cam_cfg = config["camera"]
    with Camera(cam_cfg["device_index"], cam_cfg["resolution"]) as cam:
        print(f"Collecting samples for zone '{zone_name}'")
        print(f"ROI: {bbox}")
        print(f"Keys: {', '.join(f'{k}={v}' for k, v in key_map.items())}, q=quit")
        print(f"Saving to: {csv_path}\n")

        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["label", "h_mean", "s_mean", "v_mean", "h_std", "s_std", "v_std"])

            count = 0
            while True:
                frame = cam.read()

                # Draw ROI on display
                display = frame.copy()
                x1, y1, x2, y2 = bbox
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(display, f"{zone_name} [{count} samples]", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.imshow(f"Collect - {zone_name}", display)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

                key_char = chr(key) if key < 128 else None
                if key_char in key_map:
                    roi_image = extract_roi(frame, bbox)
                    if roi_image.size == 0:
                        print("Empty ROI, skipping")
                        continue

                    feats = extract_hsv_features(roi_image)
                    label = key_map[key_char]
                    writer.writerow([label] + feats)
                    f.flush()
                    count += 1
                    print(f"  [{count}] {label}: {[round(v, 1) for v in feats]}")

    cv2.destroyAllWindows()
    print(f"\nCollected {count} samples for '{zone_name}'")


def train_model(config, zone_name):
    if zone_name not in config["zones"]:
        print(f"Zone '{zone_name}' not found in config. Run calibrate.py first.")
        return

    zone = config["zones"][zone_name]
    csv_path = f"training_data/{zone_name}_samples.csv"

    if not os.path.exists(csv_path):
        print(f"No training data found at {csv_path}. Run 'collect' first.")
        return

    # Load CSV
    features_list = []
    labels_list = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            feats = [float(row[k]) for k in ["h_mean", "s_mean", "v_mean", "h_std", "s_std", "v_std"]]
            features_list.append(feats)
            labels_list.append(row["label"])

    features_arr = np.array(features_list)
    labels_arr = np.array(labels_list)
    n_neighbors = config["classifier"]["n_neighbors"]

    print(f"Training '{zone_name}' model:")
    print(f"  Samples: {len(labels_arr)}")
    print(f"  Labels: {dict(zip(*np.unique(labels_arr, return_counts=True)))}")
    print(f"  k-NN neighbors: {n_neighbors}")

    # Cross-validation
    accuracy = evaluate(features_arr, labels_arr, n_neighbors)
    if accuracy >= 0:
        print(f"  Cross-validation accuracy: {accuracy:.2%}")
    else:
        print("  Not enough samples for cross-validation")

    # Train and save
    model = train(features_arr, labels_arr, n_neighbors)
    model_path = zone["model_path"]
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    save_model(model, model_path)
    print(f"  Model saved to: {model_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train color classifier")
    sub = parser.add_subparsers(dest="command", required=True)

    collect_cmd = sub.add_parser("collect", help="Collect training samples")
    collect_cmd.add_argument("--zone", required=True, help="Zone name (e.g. display, diode)")

    train_cmd = sub.add_parser("train", help="Train model from collected samples")
    train_cmd.add_argument("--zone", required=True, help="Zone name (e.g. display, diode)")

    args = parser.parse_args()

    try:
        with open("config.json") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config.json: {e}")
        raise SystemExit(1)

    if args.command == "collect":
        collect_samples(config, args.zone)
    elif args.command == "train":
        train_model(config, args.zone)
