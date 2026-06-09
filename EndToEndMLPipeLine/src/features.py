"""
src/features.py
---------------
TF-IDF feature engineering for the SA spam/ham classifier.

Extracted from notebook §5. The vectorizer parameters come from
configs/config.yaml so they can be tuned without touching source code.

Critical rule: the vectorizer must only ever be fit on training data.
It is saved to MLflow alongside the model so that inference always
uses the exact vocabulary the model was trained on.
"""

from sklearn.feature_extraction.text import TfidfVectorizer


def build_vectorizer(
    max_features: int = 10000,
    ngram_range: tuple = (1, 2),
    sublinear_tf: bool = True,
    min_df: int = 2,
    max_df: float = 0.95,
) -> TfidfVectorizer:
    """
    Build a TfidfVectorizer with the parameters used in notebook §5.

    Notebook used max_features=5000. Default here is 10000 (set in
    config.yaml under features.max_features). All other defaults
    match the notebook exactly.

    Parameters
    ----------
    max_features : vocabulary size cap (notebook: 5000, config default: 10000)
    ngram_range  : (1, 2) = unigrams + bigrams, same as notebook
    sublinear_tf : apply log normalisation to term frequencies
    min_df       : ignore terms in fewer than this many documents
    max_df       : ignore terms in more than this fraction of docs 

    Returns
    -------
    Unfitted TfidfVectorizer — caller must call .fit_transform() on training
    data only, then .transform() on test/inference data.
    """
    return TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        sublinear_tf=sublinear_tf,
        min_df=min_df,
        max_df=max_df,
    )