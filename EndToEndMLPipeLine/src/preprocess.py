"""
src/preprocess.py
-----------------
Text preprocessing for the SA spam/ham classifier.

Direct translation of preprocess_text() from notebook §4.
One change from the notebook: WordNetLemmatizer and the stopwords set
are created at module level (once on import) instead of inside the
function (once per email call). On 100,000 emails this matters.

All SA-specific patterns are preserved verbatim from the notebook.
"""

import re
import string

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def _ensure_nltk_resource(resource_path: str) -> None:
    """Download an NLTK resource if it is not already available."""
    try:
        nltk.data.find(resource_path)
    except LookupError:
        nltk.download(resource_path.split("/")[-1], quiet=True)


# ── Created ONCE when this module is imported ─────────────────────────────────
# Notebook had these inside preprocess_text(), creating a new object
# for every single email. Moving them here costs nothing extra.
_ensure_nltk_resource("corpora/stopwords")
_ensure_nltk_resource("corpora/wordnet")
_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))


def combine_email(subject: str, body: str) -> str:
    """Combine email subject and body into a single text string."""
    if pd.isna(subject) and pd.isna(body):
        return ""
    if pd.isna(subject):
        return str(body)
    if pd.isna(body):
        return str(subject)
    return f"{subject} {body}"


def preprocess_text(text: str) -> str:
    """
    Clean a single email string.

    Handles South African-specific patterns: local phone numbers
    and Rand currency amounts.

    Parameters
    ----------
    text : raw email text (subject + body combined, or either alone)

    Returns
    -------
    Cleaned, lemmatised string ready for TF-IDF vectorisation.
    Returns empty string for null/empty input.
    """
    if pd.isna(text):
        return ""

    # 1. Lowercase  (notebook step 1)
    text = text.lower()

    # 2. Remove URLs  (notebook step 2)
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

    # 3. Remove email addresses  (notebook step 2)
    text = re.sub(r"\S+@\S+", "", text)

    # 4. Remove SA phone numbers  (notebook step 2)
    #    Format: 082 123 4567 / 082-123-4567 / 0821234567
    text = re.sub(r"\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b", "", text)
    text = re.sub(r"\b0\d{9}\b", "", text)

    # 5. Remove currency symbols and amounts  (notebook step 3)
    #    Catches R500, R 1,000, $50, £20, €30
    text = re.sub(r"[R$£€]\s?\d+[,\d]*", "", text)

    # 6. Remove remaining numbers  (notebook step 3)
    text = re.sub(r"\d+", "", text)

    # 7. Remove punctuation  (notebook step 4)
    text = text.translate(str.maketrans("", "", string.punctuation))

    # 8. Remove extra whitespace  (notebook step 4)
    text = " ".join(text.split())

    # 9. Remove stopwords and short tokens  (notebook step 5)
    words = [w for w in text.split() if w not in _stop_words and len(w) > 2]

    # 10. Lemmatise  (notebook step 6)
    words = [_lemmatizer.lemmatize(w) for w in words]

    return " ".join(words)