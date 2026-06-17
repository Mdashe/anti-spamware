"""
src/train.py
------------
Model training for the SA spam/ham classifier.

Consolidates notebook §6 (LR, NB, SVM trained individually) and
notebook §7 (VotingClassifier ensemble) into a single function.

Key change from notebook: the notebook trains each model individually
in §6 (three .fit() calls), then creates brand-new instances and
trains them all again inside VotingClassifier in §7 — six total fits.
Here VotingClassifier.fit() trains all sub-estimators in one call.
The three individual models are accessible via ensemble.estimators_.

All hyperparameters match the notebook exactly:
  LR:  C=1.0, solver='liblinear', max_iter=1000
  NB:  alpha=1.0
  SVM: C=1.0, max_iter=1000 (LinearSVC — no predict_proba)
  Ensemble: hard voting (required for LinearSVC compatibility)
"""

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

# Sub-models available via ensemble.estimators_
# No separate lr/nb/svm pkl files needed


def train_models(X_train, y_train, random_state: int = 42) -> dict:
    """
    Train LR, NB, SVM, and their VotingClassifier ensemble.

    Returns all four in a dict so callers can access any of them
    without relying on notebook globals.

    Parameters
    ----------
    X_train      : sparse TF-IDF matrix from features.build_vectorizer()
    y_train      : integer-encoded labels (0=ham, 1=spam)
    random_state : must match config.yaml models.random_state

    Returns
    -------
    dict with keys: 'lr', 'nb', 'svm', 'ensemble'
    All four are fitted. Sub-models also accessible via
    ensemble.estimators_ (list of (name, estimator) tuples).
    """
    # ── Individual models (notebook §6 hyperparameters) ───────────────────────
    # after
    # remove n_jobs=-1
    lr = LogisticRegression(
    max_iter=1000, C=1.0,
    solver='liblinear',
    random_state=random_state
    )
    nb = MultinomialNB(alpha=1.0)   

    svm = LinearSVC(
        C=1.0,
        max_iter=1000,
        random_state=random_state, 
    )

    # ── Ensemble (notebook §7) ────────────────────────────────────────────────
    # hard voting is required because LinearSVC has no predict_proba.
    # VotingClassifier.fit() trains lr, nb, svm internally — ONE fit call,
    # not the six separate fits the notebook used.
    ensemble = VotingClassifier(
        estimators=[
            ("lr",  lr),
            ("nb",  nb),
            ("svm", svm),
        ],
        voting="hard",
        # Use single-process fit to avoid scipy/numpy writeback-if-copy
        # errors that occur when sharing sparse arrays across processes.
        n_jobs=1,
    )
    ensemble.fit(X_train, y_train)
    # VotingClassifier.fit() trains cloned sub-estimators. The fitted
    # estimators are available via `ensemble.named_estimators_` mapping
    # names to fitted estimator instances.
    fitted = getattr(ensemble, "named_estimators_", {})

    return {
        "lr": fitted.get("lr", lr),
        "nb": fitted.get("nb", nb),
        "svm": fitted.get("svm", svm),
        "ensemble": ensemble,
    }


def log_run(models: dict, vectorizer, metrics: dict, params: dict) -> str:
    """
    Log a completed training run to MLflow.

    Replaces the notebook §10 pickle.dump() block. Saves only the
    ensemble and vectorizer — the two artefacts needed for inference.
    Individual sub-models are accessible via ensemble.estimators_.

    Parameters
    ----------
    models     : return value of train_models()
    vectorizer : fitted TfidfVectorizer from features.build_vectorizer()
    metrics    : dict with keys f1, precision, recall, accuracy
    params     : dict of hyperparameters (from config.yaml models section)

    Returns
    -------
    MLflow run_id string
    """
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(models["ensemble"], "ensemble_model")
        mlflow.sklearn.log_model(vectorizer,         "tfidf_vectorizer")
        return run.info.run_id


def register_best_model(run_id: str, metrics: dict, thresholds: dict) -> None:
    """
    Promote a trained model to MLflow Staging if it passes all thresholds.

    Only registers models that exceed every threshold in config.yaml.
    A model that regresses never enters the registry.

    Thresholds checked:
      - f1        >= thresholds['min_f1']
      - precision >= thresholds['min_precision']
      - recall    >= thresholds['min_recall']
    """
    passes = (
        metrics["f1"] >= thresholds["min_f1"]
        and metrics["precision"] >= thresholds["min_precision"]
        and metrics["recall"] >= thresholds["min_recall"]
    )

    if passes:
        result = mlflow.register_model(
            f"runs:/{run_id}/ensemble_model",
            "spam_ensemble",
        )
        MlflowClient().transition_model_version_stage(
            name="spam_ensemble",
            version=result.version,
            stage="Staging",
        )
        print(f"Model v{result.version} promoted to Staging  "
              f"(F1={metrics['f1']:.4f})")
    else:
        print("Model did NOT meet thresholds — not registered.")
        print(f"  F1={metrics['f1']:.4f}  "
              f"P={metrics['precision']:.4f}  "
              f"R={metrics['recall']:.4f}")
        print(f"  Required: F1>={thresholds['min_f1']}  "
              f"P>={thresholds['min_precision']}  "
              f"R>={thresholds['min_recall']}")