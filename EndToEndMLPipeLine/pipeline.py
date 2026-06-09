"""Pipeline orchestration for the anti-spam classifier.

This module defines Prefect tasks for loading data, running exploratory
analysis, preprocessing text, featurizing data, and training/evaluating
models with MLflow logging.
"""

import yaml, pandas as pd, mlflow, mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from prefect import flow, task, get_run_logger
from src.preprocess import preprocess_text
from src.features import build_vectorizer
from src.train import train_models, log_run
from src import evaluate
from src.eda import check_data_quality, plot_eda

mlflow.set_tracking_uri("http://127.0.0.1:5000")

with open('configs/configs.yaml') as f:
    CFG = yaml.safe_load(f)

@task
def load_data():
    """Load raw dataset into a pandas DataFrame.

    Returns:
        pandas.DataFrame: Loaded raw data from the configured path.
    """
    logger = get_run_logger()
    df = pd.read_csv(CFG['data']['raw_path'])
    logger.info(f'Loaded {len(df):,} rows')
    return df

@task
def run_eda(df):
    """Run exploratory data analysis and return cleaned data.

    Args:
        df (pandas.DataFrame): Raw dataset to analyze.

    Returns:
        pandas.DataFrame: Cleaned DataFrame after data quality checks.
    """
    logger = get_run_logger()
    report, df_clean = check_data_quality(df)   # raises on bad data
    logger.info(f'Missing: {report["missing_counts"]}')
    logger.info(f'Duplicates: {report["duplicate_rows"]}')
    logger.info(f'Class counts: {report["class_counts"]}')
    logger.info(f'Imbalance ratio: {report["imbalance_ratio"]}')
    plot_eda(df_clean)   # saves EDA PNGs to reports/figures/
    return df_clean

@task
def preprocess(df):
    """Preprocess raw email text and produce cleaned tokens.

    Args:
        df (pandas.DataFrame): Raw dataset containing email subject and body.

    Returns:
        pandas.DataFrame: Dataset with a processed text column, filtered to
        remove empty values.
    """
    from src.preprocess import combine_email
    df = df.copy()
    df['text'] = df.apply(
        lambda r: combine_email(r['subject'], r['body']), axis=1
    )
    df['processed_text'] = df['text'].apply(preprocess_text)
    return df[df['processed_text'].str.len() > 0]

@task
def featurise(df):
    """Create training/test splits and vectorize processed text.

    Args:
        df (pandas.DataFrame): Dataset containing processed text and labels.

    Returns:
        tuple: Transformed training/test matrices, label arrays, and vectorizer.
    """
    le = LabelEncoder()
    y  = le.fit_transform(df['label'])
    X_tr, X_te, y_tr, y_te = train_test_split(
        df['processed_text'], y,
        test_size=CFG['data']['test_size'],
        random_state=CFG['models']['random_state'],
        stratify=y
    )
    vec = build_vectorizer(
        max_features=CFG['features']['max_features'],
        ngram_range=tuple(CFG['features']['ngram_range'])
    )
    # Ensure returned sparse matrices are writable copies — prevents scipy
    # "WRITEBACKIFCOPY base is read-only" errors when operating in parallel.
    X_tr_mat = vec.fit_transform(X_tr).tocsr().copy()
    X_te_mat = vec.transform(X_te).tocsr().copy()
    return X_tr_mat, X_te_mat, y_tr, y_te, vec

@task
def train_and_evaluate(X_tr, X_te, y_tr, y_te, vec):
    """Train models, evaluate performance, and log results to MLflow.

    Args:
        X_tr: Training features.
        X_te: Test features.
        y_tr: Training labels.
        y_te: Test labels.
        vec: Fitted vectorizer for the text data.

    Returns:
        dict: Evaluation metrics for the ensemble model.
    """
    models = train_models(X_tr, y_tr, CFG['models']['random_state'])
    y_pred = models['ensemble'].predict(X_te)
    metrics = evaluate.compute_metrics(y_te, y_pred)

    # Scores for ROC (mirrors your notebook §8)
    lr_scores  = models['lr'].predict_proba(X_te)[:, 1]
    nb_scores  = models['nb'].predict_proba(X_te)[:, 1]
    svm_scores = models['svm'].decision_function(X_te)
    preds = {'LR': models['lr'].predict(X_te),
             'NB': models['nb'].predict(X_te),
             'SVM': models['svm'].predict(X_te),
             'Ensemble': y_pred}

    # Generate charts — same seaborn/matplotlib code as notebook
    fig_cm   = evaluate.plot_confusion_matrices(preds, y_te)
    fig_roc  = evaluate.plot_roc_curves(
        {'LR':lr_scores,'NB':nb_scores,'SVM':svm_scores}, y_te)
    fig_feat = evaluate.plot_feature_importance(models['lr'], vec)

    # Log everything to MLflow — replaces notebook §10 pickle block
    with mlflow.start_run():
        mlflow.log_params(CFG['models'])
        mlflow.log_metrics(metrics)
        mlflow.log_artifact('reports/figures/confusion_matrices.png','evaluation')
        mlflow.log_artifact('reports/figures/roc_curves.png','evaluation')
        mlflow.log_artifact('reports/figures/feature_importance.png','evaluation')
        mlflow.sklearn.log_model(models['ensemble'], name='ensemble_model')
        mlflow.sklearn.log_model(vec, name='tfidf_vectorizer')

    import matplotlib.pyplot as plt
    plt.close('all')  # mandatory — prevents memory leak
    return metrics

@flow(name='spam-classifier-training')
def training_pipeline():
    df = load_data()
    df = run_eda(df)          # quality gate BEFORE training
    df = preprocess(df)
    X_tr, X_te, y_tr, y_te, vec = featurise(df)
    metrics = train_and_evaluate(X_tr, X_te, y_tr, y_te, vec)
    print('Done:', metrics)


if __name__ == '__main__':
    training_pipeline()
