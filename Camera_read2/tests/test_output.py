import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import pytest
import output
from output import log_event


@pytest.fixture(autouse=True)
def temp_log_path(tmp_path):
    original = output.LOG_PATH
    output.LOG_PATH = str(tmp_path / "events.json")
    yield tmp_path
    output.LOG_PATH = original


def test_log_event_returns_valid_json():
    line = log_event("display", "red", "error")
    record = json.loads(line)
    assert record["zone"] == "display"
    assert record["color"] == "red"
    assert record["status"] == "error"
    assert record["type"] == "change"
    assert "timestamp" in record


def test_log_event_with_prev_color():
    line = log_event("diode", "green", "ok", prev_color="red")
    record = json.loads(line)
    assert record["prev_color"] == "red"


def test_log_event_without_prev_color():
    line = log_event("diode", "green", "ok")
    record = json.loads(line)
    assert "prev_color" not in record


def test_log_event_with_features():
    feats = [120.5, 200.3, 180.7, 5.2, 10.1, 8.9]
    line = log_event("display", "yellow", "warning", features=feats)
    record = json.loads(line)
    assert "features" in record
    assert len(record["features"]) == 6


def test_log_event_custom_type():
    line = log_event("display", "red", "error", event_type="heartbeat")
    record = json.loads(line)
    assert record["type"] == "heartbeat"


def test_log_event_features_rounded():
    feats = [120.555, 200.333, 180.777, 5.222, 10.111, 8.999]
    line = log_event("display", "red", "error", features=feats)
    record = json.loads(line)
    for v in record["features"]:
        # Should have at most 2 decimal places
        assert v == round(v, 2)


def test_log_event_writes_to_file(temp_log_path):
    log_event("diode_1", "red", "error", prev_color="green")
    log_event("diode_1", "green", "ok", prev_color="red")

    with open(output.LOG_PATH) as f:
        events = json.load(f)

    assert len(events) == 2
    assert events[0]["color"] == "red"
    assert events[0]["status"] == "error"
    assert events[0]["prev_color"] == "green"
    assert events[1]["color"] == "green"
    assert events[1]["status"] == "ok"


def test_log_file_creates_directory(tmp_path):
    output.LOG_PATH = str(tmp_path / "subdir" / "events.json")
    log_event("diode_1", "red", "error")
    assert os.path.exists(output.LOG_PATH)
