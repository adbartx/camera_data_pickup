import json
import os
from datetime import datetime

LOG_PATH = "logs/events.json"


def _append_to_file(record):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            events = json.load(f)
    else:
        events = []

    events.append(record)

    with open(LOG_PATH, "w") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)


def log_event(zone_name, color, status, prev_color=None, event_type="change", features=None):
    record = {
        "timestamp": datetime.now().isoformat(timespec="milliseconds"),
        "zone": zone_name,
        "color": color,
        "status": status,
        "type": event_type
    }
    if prev_color is not None:
        record["prev_color"] = prev_color
    if features is not None:
        record["features"] = [round(v, 2) for v in features]

    line = json.dumps(record)
    print(line, flush=True)
    _append_to_file(record)
    return line
