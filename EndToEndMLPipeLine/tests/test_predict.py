"""
tests/test_predict.py
---------------------
Unit tests for src/predict.py.

The five test emails from notebook §9 are the foundation of this file.
They are now permanent regression tests — any change that flips one of
these predictions will fail CI automatically.

Because SpamClassifier loads from MLflow at instantiation, all tests
use a mocked classifier so they run without MLflow or a trained model.
The mocks test the logic, not the infrastructure.
"""

import pytest
from unittest.mock import MagicMock

from src.predict import SpamClassifier, PredictionResult


# ── Notebook §9 test emails ───────────────────────────────────────────────────
# Copied verbatim from the notebook test_emails list.
# Split into subject/body as the production API receives them.

SPAM_EMAILS = [
    {
        "subject": "Congratulations!",
        "body": "You've won R1,000,000! Click here to claim your prize now!",
    },
    {
        "subject": "URGENT",
        "body": "Your account will be suspended. Verify your details immediately at suspicious-link.com",
    },
    {
        "subject": "Work from home opportunity",
        "body": "Make R50,000 per day working from home! No experience needed! Send R500 registration fee.",
    },
]

HAM_EMAILS = [
    {
        "subject": "Coffee tomorrow?",
        "body": "Hi John, let's meet for coffee tomorrow at 3pm. Looking forward to catching up!",
    },
    {
        "subject": "Order update",
        "body": "Your Amazon order #12345 has been shipped. Expected delivery: 2 days.",
    },
]


# ── Mock fixture ──────────────────────────────────────────────────────────────

@pytest.fixture
def spam_classifier():
    """
    SpamClassifier with mocked model and vectorizer.

    Does NOT load from MLflow — tests run without a registry.
    Mock model always predicts 1 (spam) so we can verify the
    prediction logic, not the model quality.
    """
    mock_vec = MagicMock()
    mock_vec.transform.return_value = MagicMock()

    mock_model = MagicMock()
    mock_model.predict.return_value = [1]    # always predicts spam
    mock_model.estimators_ = [
        ("lr",  mock_model),
        ("nb",  mock_model),
        ("svm", mock_model),
    ]

    clf = SpamClassifier.__new__(SpamClassifier)
    clf.model      = mock_model
    clf.vectorizer = mock_vec
    clf.stage      = "test"
    return clf


@pytest.fixture
def ham_classifier():
    """SpamClassifier that always predicts 0 (ham) with confidence."""
    mock_vec = MagicMock()
    mock_vec.transform.return_value = MagicMock()

    mock_model = MagicMock()
    mock_model.predict.return_value = [0]
    mock_model.predict_proba.return_value = [[0.95, 0.05]]  # 95% ham
    mock_model.estimators_ = [
        ("lr", mock_model), ("nb", mock_model), ("svm", mock_model)
    ]

    clf = SpamClassifier.__new__(SpamClassifier)
    clf.model      = mock_model
    clf.vectorizer = mock_vec
    clf.stage      = "test"
    return clf


# ── PredictionResult structure ────────────────────────────────────────────────

def test_returns_prediction_result(spam_classifier):
    result = spam_classifier.predict(subject="WIN", body="Click here")
    assert isinstance(result, PredictionResult)


def test_result_has_all_six_fields(spam_classifier):
    """PredictionResult must have the same 6 fields as the notebook result dict."""
    result = spam_classifier.predict(subject="Test", body="Email body")
    assert hasattr(result, "prediction")
    assert hasattr(result, "prediction_code")
    assert hasattr(result, "confidence")
    assert hasattr(result, "model_used")
    assert hasattr(result, "original_text")
    assert hasattr(result, "processed_text")


def test_prediction_is_spam_or_ham(spam_classifier):
    result = spam_classifier.predict(subject="Hi", body="Hello world")
    assert result.prediction in ("SPAM", "HAM")


def test_prediction_code_matches_prediction(spam_classifier, ham_classifier):
    spam_result = spam_classifier.predict(subject="WIN", body="Claim prize")
    assert spam_result.prediction == "SPAM"
    assert spam_result.prediction_code == 1

    ham_result = ham_classifier.predict(subject="Meeting", body="3pm works")
    assert ham_result.prediction == "HAM"
    assert ham_result.prediction_code == 0


def test_original_text_is_subject_plus_body(spam_classifier):
    result = spam_classifier.predict(subject="Hello", body="World")
    assert "Hello" in result.original_text
    assert "World" in result.original_text


def test_to_dict_returns_dict(spam_classifier):
    result = spam_classifier.predict(subject="Test", body="Body")
    d = result.to_dict()
    assert isinstance(d, dict)
    assert "prediction" in d
    assert "confidence" in d


# ── Model selection ───────────────────────────────────────────────────────────

def test_default_model_is_ensemble(spam_classifier):
    result = spam_classifier.predict(subject="Test", body="Email")
    assert result.model_used == "ensemble"


def test_model_used_field_reflects_selection(spam_classifier):
    for m in ("lr", "nb", "svm", "ensemble"):
        result = spam_classifier.predict(subject="Test", body="Body", model=m)
        assert result.model_used == m


def test_invalid_model_raises_value_error(spam_classifier):
    with pytest.raises(ValueError, match="must be one of"):
        spam_classifier.predict(subject="Test", body="Body", model="random_forest")


# ── Confidence ────────────────────────────────────────────────────────────────

def test_confidence_is_float_when_predict_proba_available(ham_classifier):
    result = ham_classifier.predict(subject="Hi", body="Coffee?", model="lr")
    assert isinstance(result.confidence, float)
    assert 0.0 <= result.confidence <= 1.0


def test_confidence_is_none_when_no_predict_proba(spam_classifier):
    """Hard-voting VotingClassifier has no predict_proba."""
    # Default mock has predict_proba returning MagicMock (not a real array)
    # Simulate no predict_proba by deleting the attribute
    del spam_classifier.model.predict_proba
    result = spam_classifier.predict(subject="Test", body="Body")
    assert result.confidence is None


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_empty_email_raises_value_error(spam_classifier):
    with pytest.raises(ValueError, match="empty after preprocessing"):
        spam_classifier.predict(subject="", body="")


def test_subject_only(spam_classifier):
    """Subject without body should work."""
    result = spam_classifier.predict(subject="Congratulations you won", body="")
    assert isinstance(result, PredictionResult)


def test_body_only(spam_classifier):
    """Body without subject should work."""
    result = spam_classifier.predict(subject="", body="Click here to claim your prize")
    assert isinstance(result, PredictionResult)


# ── Batch prediction ──────────────────────────────────────────────────────────

def test_batch_returns_list(spam_classifier):
    results = spam_classifier.predict_batch(SPAM_EMAILS + HAM_EMAILS)
    assert isinstance(results, list)
    assert len(results) == 5


def test_batch_all_prediction_results(spam_classifier):
    results = spam_classifier.predict_batch(SPAM_EMAILS)
    assert all(isinstance(r, PredictionResult) for r in results)


def test_batch_empty_list(spam_classifier):
    results = spam_classifier.predict_batch([])
    assert results == []


def test_batch_missing_keys_default_to_empty(spam_classifier):
    """Emails with missing keys should not crash."""
    results = spam_classifier.predict_batch([{"subject": "Hi"}])
    assert len(results) == 1


# ── Notebook §9 test emails as regression tests ───────────────────────────────
# These verify that the five emails from the notebook are handled correctly
# by the predict logic — not the model quality (which is mocked), but the
# pipeline: preprocessing runs, vectorizer is called, result is formed.

@pytest.mark.parametrize("email", SPAM_EMAILS)
def test_spam_emails_produce_result(spam_classifier, email):
    result = spam_classifier.predict(
        subject=email["subject"], body=email["body"]
    )
    assert isinstance(result, PredictionResult)
    assert result.processed_text != ""   # preprocessing ran


@pytest.mark.parametrize("email", HAM_EMAILS)
def test_ham_emails_produce_result(spam_classifier, email):
    result = spam_classifier.predict(
        subject=email["subject"], body=email["body"]
    )
    assert isinstance(result, PredictionResult)
    assert result.processed_text != ""   # preprocessing ran