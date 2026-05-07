import argparse
import json
from monitor import ColorMonitor


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Camera color monitor")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    args = parser.parse_args()

    try:
        with open(args.config) as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}")
        raise SystemExit(1)

    if not config["zones"]:
        print("No zones configured. Run calibrate.py first.")
        raise SystemExit(1)

    monitor = ColorMonitor(config)
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
