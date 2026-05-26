import sys
import numpy as np
from sklearn.metrics import roc_auc_score

from src.exception import CustomException
from src.logger import logging


def evaluate_models(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    models: dict,
) -> dict:
    try:
        report = {}
        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred_proba = model.predict_proba(X_val)[:, 1]
            score = roc_auc_score(y_val, y_pred_proba)
            report[name] = score
            logging.info(f"{name} — validation ROC-AUC: {score:.4f}")
        return report
    except Exception as e:
        raise CustomException(e, sys)
