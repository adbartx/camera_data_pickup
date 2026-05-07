import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tempfile
import numpy as np
from classifier import train, predict, save_model, load_model, evaluate


def _sample_data():
    # Simple 2-class data: red-ish vs green-ish HSV features
    features = np.array([
        [0, 200, 200, 5, 10, 10],   # red
        [2, 210, 190, 4, 12, 8],    # red
        [5, 195, 205, 6, 11, 9],    # red
        [60, 200, 200, 5, 10, 10],  # green
        [58, 210, 190, 4, 12, 8],   # green
        [63, 195, 205, 6, 11, 9],   # green
    ])
    labels = np.array(["red", "red", "red", "green", "green", "green"])
    return features, labels


def test_train_returns_model():
    features, labels = _sample_data()
    model = train(features, labels, n_neighbors=3)
    assert model is not None


def test_predict_returns_string():
    features, labels = _sample_data()
    model = train(features, labels, n_neighbors=3)
    result = predict(model, [1, 200, 200, 5, 10, 10])
    assert isinstance(result, str)
    assert result in ("red", "green")


def test_predict_red():
    features, labels = _sample_data()
    model = train(features, labels, n_neighbors=3)
    result = predict(model, [1, 200, 200, 5, 10, 10])
    assert result == "red"


def test_predict_green():
    features, labels = _sample_data()
    model = train(features, labels, n_neighbors=3)
    result = predict(model, [60, 200, 200, 5, 10, 10])
    assert result == "green"


def test_save_and_load_model():
    features, labels = _sample_data()
    model = train(features, labels, n_neighbors=3)

    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        path = f.name

    try:
        save_model(model, path)
        loaded = load_model(path)
        result = predict(loaded, [1, 200, 200, 5, 10, 10])
        assert result == "red"
    finally:
        os.unlink(path)


def test_evaluate_returns_accuracy():
    # Need at least 5 samples per class for 5-fold CV
    features = np.array([
        [0, 200, 200, 5, 10, 10],
        [2, 210, 190, 4, 12, 8],
        [5, 195, 205, 6, 11, 9],
        [1, 205, 195, 5, 11, 10],
        [3, 198, 202, 4, 10, 9],
        [60, 200, 200, 5, 10, 10],
        [58, 210, 190, 4, 12, 8],
        [63, 195, 205, 6, 11, 9],
        [61, 205, 195, 5, 11, 10],
        [59, 198, 202, 4, 10, 9],
    ])
    labels = np.array(["red"] * 5 + ["green"] * 5)
    accuracy = evaluate(features, labels, n_neighbors=3)
    assert 0.0 <= accuracy <= 1.0


def test_evaluate_too_few_samples():
    features = np.array([[1, 2, 3, 4, 5, 6]])
    labels = np.array(["red"])
    accuracy = evaluate(features, labels)
    assert accuracy == -1.0
