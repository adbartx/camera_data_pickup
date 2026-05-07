import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
import joblib


def train(features, labels, n_neighbors=3) -> KNeighborsClassifier:
    model = KNeighborsClassifier(n_neighbors=n_neighbors)
    model.fit(features, labels)
    return model


def evaluate(features, labels, n_neighbors=3) -> float:
    model = KNeighborsClassifier(n_neighbors=n_neighbors)
    n_samples = len(labels)
    cv_folds = min(5, n_samples)
    if cv_folds < 2:
        return -1.0
    scores = cross_val_score(model, features, labels, cv=cv_folds)
    return float(np.mean(scores))


def save_model(model, path):
    joblib.dump(model, path)


def load_model(path) -> KNeighborsClassifier:
    return joblib.load(path)


def predict(model, features) -> str:
    result = model.predict([features])
    return str(result[0])
