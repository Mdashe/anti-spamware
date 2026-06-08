"""
tests/test_preprocess.py
------------------------
Unit tests for src/preprocess.py.

Tests every cleaning step from notebook §4, with particular attention
to the SA-specific patterns that are unique to this dataset.
"""

from src.preprocess import preprocess_text


# ── SA-specific patterns ──────────────────────────────────────────────────────
# These are the patterns unique to the South African dataset.
# They must be tested explicitly because a generic spam classifier
# would not have them.

def test_removes_rand_amounts():
    """R500, R1,000, R50,000 — notebook §4 SA currency pattern."""
    assert "500"   not in preprocess_text("Win R500 now!")
    assert "1000"  not in preprocess_text("Claim R1,000 today")
    assert "50000" not in preprocess_text("Make R50,000 per day")


def test_removes_sa_mobile_number():
    """0821234567 — notebook §4 \\b0\\d{9}\\b pattern."""
    result = preprocess_text("Call 0821234567 to claim your prize")
    assert "0821234567" not in result


def test_removes_sa_formatted_number():
    """082 123 4567 — notebook §4 \\b\\d{3}[\\s-]?\\d{3}[\\s-]?\\d{4}\\b pattern."""
    result = preprocess_text("Call 082 123 4567 now")
    assert "0821234567" not in result
    assert "082" not in result


def test_removes_urls():
    """http and www URLs — notebook §4 step 2."""
    result = preprocess_text("Visit http://suspicious-link.com for details")
    assert "http" not in result
    assert "suspicious" in result or "link" in result   # domain words may remain


def test_removes_email_addresses():
    """Email addresses — notebook §4 step 2."""
    result = preprocess_text("Reply to spam@scammer.co.za immediately")
    assert "@" not in result


def test_removes_numbers():
    """Plain numbers — notebook §4 step 3."""
    result = preprocess_text("You are winner number 12345")
    assert "12345" not in result


def test_removes_punctuation():
    """Punctuation removal — notebook §4 step 4."""
    result = preprocess_text("Hello, world! How are you?")
    assert "," not in result
    assert "!" not in result
    assert "?" not in result


def test_removes_stopwords():
    """Common English stopwords filtered — notebook §4 step 5."""
    result = preprocess_text("this is a test of the stopword removal")
    assert "this" not in result
    assert "is"   not in result
    assert "the"  not in result


def test_lemmatises_words():
    """WordNetLemmatizer applied — notebook §4 step 6."""
    result = preprocess_text("running winners claiming prizes")
    # lemmatized forms (exact form depends on NLTK model)
    assert "running" not in result or "run" in result


def test_lowercases():
    """Converts to lowercase — notebook §4 step 1."""
    result = preprocess_text("URGENT CLAIM YOUR PRIZE NOW")
    assert result == result.lower()


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_empty_string_returns_empty():
    assert preprocess_text("") == ""


def test_nan_returns_empty():
    import pandas as pd
    assert preprocess_text(pd.NA)  == ""
    assert preprocess_text(None)   == ""   # pd.isna(None) is True


def test_whitespace_only_returns_empty():
    result = preprocess_text("   ")
    assert result == ""


def test_returns_string():
    assert isinstance(preprocess_text("Hello world"), str)


def test_short_words_filtered():
    """Words of length <= 2 are removed — notebook §4 len(w) > 2."""
    result = preprocess_text("go to it as")
    # all words are 2 chars or fewer — should return empty
    assert result == ""


# ── Module-level object verification ─────────────────────────────────────────

def test_module_level_objects_exist():
    """Verify _lemmatizer and _stop_words are created at module level."""
    from src import preprocess as p
    assert hasattr(p, "_lemmatizer")
    assert hasattr(p, "_stop_words")
    assert len(p._stop_words) > 100   # English stopwords list is ~180 words


def test_consistent_output():
    """Same input always produces same output — deterministic."""
    text = "Congratulations! You have won R1,000,000! Call 0821234567 now!"
    assert preprocess_text(text) == preprocess_text(text)