"""
src/predict.py
--------------
Inference for the SA spam/ham classifier.

Direct translation of notebook §9 predict_spam() function.

The logic is identical to the notebook:
  1. Combine subject + body
  2. Call preprocess_text()
  3. Vectorise with the saved TfidfVectorizer
  4. Call the selected model's .predict()
  5. Get confidence via .predict_proba() if available (LR, NB)
     or None if not (SVM/LinearSVC, hard-voting Ensemble)
  6. Return a dict with 6 fields matching the notebook result dict

Structural changes from the notebook:
  - Models come from the MLflow registry instead of notebook globals
  - SpamClassifier class wraps the logic so it can be instantiated
    independently of any notebook session
  - PredictionResult dataclass gives the result dict type safety
  - predict_batch() added for classifying multiple emails at once
  - subject and body are separate parameters (API sends them separately)
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional

import mlflow.sklearn

from src.preprocess import preprocess_text

import mlflow
mlflow.set_tracking_uri('http://127.0.0.1:5000')


# ── Result dataclass ──────────────────────────────────────────────────────────
# Same 6 fields as the notebook §9 result dict.
# predict_spam() returned:
#   {'prediction', 'prediction_code', 'confidence',
#    'model_used', 'original_text', 'processed_text'}

@dataclass
class PredictionResult:
    prediction:      str             # 'SPAM' or 'HAM'
    prediction_code: int             # 1 = spam, 0 = ham (matches notebook encoding)
    confidence:      Optional[float] # probability of predicted class; None for SVM/Ensemble
    model_used:      str             # 'lr', 'nb', 'svm', or 'ensemble'
    original_text:   str             # raw input as received (subject + body)
    processed_text:  str             # after preprocess_text()

    def to_dict(self) -> dict:
        """Return as plain dict — used by the FastAPI response."""
        return asdict(self)


# ── Classifier ────────────────────────────────────────────────────────────────

class SpamClassifier:
    """
    Loads the production model + vectorizer from the MLflow registry
    and exposes predict() and predict_batch().

    Instantiation loads models once. Do NOT instantiate inside a
    request handler or pipeline task — load once at startup.

    Usage
    -----
        classifier = SpamClassifier()                    # loads Production
        classifier = SpamClassifier(stage='Staging')     # loads Staging for testing

        result = classifier.predict(
            subject='WIN R1,000,000!',
            body='Click here to claim your prize',
            model='ensemble',
        )
        print(result.prediction)  # 'SPAM'
        print(result.confidence)  # None (hard-voting ensemble has no predict_proba)
    """

    VALID_MODELS = ("lr", "nb", "svm", "ensemble")

    def __init__(self, stage: str = "Production") -> None:
        """
        Load ensemble model and TF-IDF vectorizer from MLflow registry.

        Parameters
        ----------
        stage : 'Production' for live serving, 'Staging' for pre-production testing.
                Must match a registered stage in the MLflow Model Registry.
        """
        self.model = mlflow.sklearn.load_model(
            f"models:/spam_ensemble/{stage}"
        )
        self.vectorizer = mlflow.sklearn.load_model(
            f"models:/tfidf_vectorizer/{stage}"
        )
        self.stage = stage

    def predict(self, subject: str = "", body:    str = "",model:   str = "ensemble",) -> PredictionResult:
        """
        Classify a single email.

        Mirrors notebook §9 predict_spam() exactly.

        Parameters
        ----------
        subject : email subject line (may be empty string)
        body    : email body text   (may be empty string)
        model   : which estimator to use — 'lr', 'nb', 'svm', or 'ensemble'
                  Default 'ensemble' matches the notebook default.

        Returns
        -------
        PredictionResult with the same 6 fields as the notebook result dict.

        Raises
        ------
        ValueError : if model is not one of VALID_MODELS
        ValueError : if email is empty after preprocessing
        """
        if model not in self.VALID_MODELS:
            raise ValueError(
                f"model must be one of {self.VALID_MODELS}, got '{model}'"
            )

        # Notebook concatenated subject + body before calling preprocess_text()
        raw_text       = (subject + " " + body).strip()
        processed_text = preprocess_text(raw_text)

        if not processed_text:
            raise ValueError(
                "Email is empty after preprocessing — nothing to classify. "
                "Check that subject and body contain actual text."
            )

        # Vectorise (notebook: text_tfidf = tfidf_vectorizer.transform([processed_text]))
        X = self.vectorizer.transform([processed_text])

        # Select estimator (notebook: model_map.get(model, ensemble_model))
        estimator = self._get_estimator(model)

        # Predict (notebook: prediction = selected_model.predict(text_tfidf)[0])
        pred_code = int(estimator.predict(X)[0])

        # Confidence (notebook: if hasattr(selected_model, 'predict_proba'):)
        if hasattr(estimator, "predict_proba"):
            probas     = estimator.predict_proba(X)[0]
            confidence = float(probas[pred_code])
        else:
            # LinearSVC and hard-voting VotingClassifier have no predict_proba
            confidence = None

        return PredictionResult(
            prediction      = "SPAM" if pred_code == 1 else "HAM",
            prediction_code = pred_code,
            confidence      = confidence,
            model_used      = model,
            original_text   = raw_text,
            processed_text  = processed_text,
        )

    def predict_batch(
        self,
        emails: list[dict],
        model:  str = "ensemble",
    ) -> list[PredictionResult]:
        """
        Classify a list of emails.

        Not in the notebook — added for production use cases where a
        mail server or batch job submits many emails in one call.

        Parameters
        ----------
        emails : list of dicts, each with 'subject' and 'body' keys.
                 Missing keys default to empty string.

        Example
        -------
            results = classifier.predict_batch([
                {'subject': 'WIN NOW', 'body': 'Click here'},
                {'subject': 'Meeting', 'body': '3pm tomorrow'},
            ])
        """
        return [
            self.predict(
                subject=e.get("subject", ""),
                body   =e.get("body",    ""),
                model  =model,
            )
            for e in emails
        ]

    def _get_estimator(self, model: str):
        """
        Return the named estimator.

        'ensemble' returns the VotingClassifier directly.
        'lr', 'nb', 'svm' pull the sub-estimator from
        VotingClassifier.estimators_ — the same objects that were fitted,
        equivalent to the notebook's lr_model / nb_model / svm_model globals.
        """
        if model == "ensemble":
            return self.model

        # VotingClassifier stores fitted sub-estimators as:
        # [(name, estimator), ...] in self.model.estimators_
        name_map = {name: est for name, est in self.model.estimators_}

        if model not in name_map:
            raise ValueError(
                f"'{model}' not found in ensemble. "
                f"Available: {list(name_map.keys())}"
            )
        return name_map[model]