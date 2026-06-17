"""
src/evaluate.py
---------------
Model evaluation for the SA spam/ham classifier.

Direct translation of notebook §8. Every chart is produced with
identical seaborn/matplotlib code from the notebook. The only
changes:
  - matplotlib.use('Agg') at the top — mandatory for Docker/CI
  - plt.show() → fig.savefig() + return fig (for MLflow logging)
  - plt.close(fig) after every save — prevents memory leaks in pipeline

Functions
---------
compute_metrics()         — scalar metrics dict (replaces notebook §8 results_df)
plot_confusion_matrices() — 2×2 seaborn heatmap grid (notebook §8)
plot_roc_curves()         — 3-model ROC comparison (notebook §8)
plot_feature_importance() — LR coefficient bar charts (notebook §8)
"""

import os

import matplotlib
matplotlib.use("Agg")   # MUST come before any other matplotlib import.
                        # Colab has a display. Docker/CI does not.
                        # Without this line the pipeline crashes with
                        # "cannot connect to X server".
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    auc,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
)

FIGURES_DIR = "reports/figures"


def _ensure_dirs() -> None:
    os.makedirs(FIGURES_DIR, exist_ok=True)


# ── Scalar metrics ─────────────────────────────────────────────────────────────

def compute_metrics(y_true, y_pred) -> dict:
    """
    Compute the four metrics shown in notebook §8 results_df.

    Returns
    -------
    dict with keys: f1, precision, recall, accuracy
    Passed to mlflow.log_metrics() in the pipeline.
    """
    return {
        "f1":        f1_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred),
        "recall":    recall_score(y_true, y_pred),
        "accuracy":  accuracy_score(y_true, y_pred),
    }


# ── Confusion matrices ─────────────────────────────────────────────────────────

def plot_confusion_matrices(models_preds: dict, y_true) -> plt.Figure:
    """
    2×2 grid of seaborn confusion matrix heatmaps.

    Mirrors notebook §8 confusion matrix cell exactly.
    plt.show() → fig.savefig() + return fig for MLflow.

    Parameters
    ----------
    models_preds : {'LR': y_pred, 'NB': y_pred, 'SVM': y_pred, 'Ensemble': y_pred}
    y_true       : ground truth labels

    Returns
    -------
    matplotlib Figure (pass to mlflow.log_figure())
    """
    _ensure_dirs()
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))

    for ax, (model_name, y_pred) in zip(axes.flat, models_preds.items()):
        cm = confusion_matrix(y_true, y_pred)

        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=["Ham", "Spam"],
            yticklabels=["Ham", "Spam"],
            cbar=True,
            ax=ax,
            annot_kws={"size": 14},
        )

        accuracy = (cm[0, 0] + cm[1, 1]) / cm.sum()
        ax.set_title(f"{model_name}\nConfusion Matrix", fontsize=14, fontweight="bold")
        ax.set_ylabel("True Label", fontsize=12)
        ax.set_xlabel("Predicted Label", fontsize=12)
        ax.text(
            1, -0.15,
            f"Accuracy: {accuracy:.4f}",
            ha="center", va="top",
            transform=ax.transAxes,
            fontsize=11, fontweight="bold",
        )

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "confusion_matrices.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)   # free memory — never skip in a pipeline
    return fig


# ── ROC curves ────────────────────────────────────────────────────────────────

def plot_roc_curves(models_proba: dict, y_true) -> plt.Figure:
    """
    3-model ROC curve comparison.

    Mirrors notebook §8 ROC cell exactly.
    SVM uses decision_function scores (no predict_proba on LinearSVC).

    Parameters
    ----------
    models_proba : {
        'LR':  predict_proba(X_test)[:, 1],   # probability of spam
        'NB':  predict_proba(X_test)[:, 1],
        'SVM': decision_function(X_test),      # decision scores, not probabilities
    }
    y_true : ground truth labels

    Returns
    -------
    matplotlib Figure (pass to mlflow.log_figure())
    """
    _ensure_dirs()
    colours = {
        "LR":  "#3498db",   # notebook used #3498db for LR
        "NB":  "#2ecc71",   # notebook used #2ecc71 for NB
        "SVM": "#e74c3c",   # notebook used #e74c3c for SVM
    }

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    for name, scores in models_proba.items():
        fpr, tpr, _ = roc_curve(y_true, scores)
        roc_auc = auc(fpr, tpr)
        ax.plot(
            fpr, tpr,
            label=f"{name} (AUC = {roc_auc:.3f})",
            linewidth=2,
            color=colours.get(name, "gray"),
        )

    # Random classifier baseline — notebook included this
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random Classifier")

    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC Curves — Model Comparison", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right", fontsize=11)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "roc_curves.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return fig


# ── Feature importance ────────────────────────────────────────────────────────

def plot_feature_importance(lr_model, vectorizer, top_n: int = 20) -> plt.Figure:
    """
    Logistic Regression coefficient bar charts — top spam and ham indicators.

    Mirrors notebook §8 feature importance cell exactly.
    Uses LR coefficients because LR is the only interpretable model
    in the ensemble (NB log-probs are less intuitive, SVM is LinearSVC).

    Parameters
    ----------
    lr_model   : fitted LogisticRegression (from train_models()['lr'])
    vectorizer : fitted TfidfVectorizer (from features.build_vectorizer())
    top_n      : number of top features to show (notebook used 20)

    Returns
    -------
    matplotlib Figure (pass to mlflow.log_figure())
    """
    _ensure_dirs()
    feature_names = vectorizer.get_feature_names_out()
    coefficients  = lr_model.coef_[0]

    # Notebook §8 exact logic
    top_spam_idx = np.argsort(coefficients)[-top_n:][::-1]
    top_ham_idx  = np.argsort(coefficients)[:top_n]

    spam_words  = [feature_names[i] for i in top_spam_idx]
    spam_scores = [coefficients[i]  for i in top_spam_idx]
    ham_words   = [feature_names[i] for i in top_ham_idx]
    ham_scores  = [abs(coefficients[i]) for i in top_ham_idx]

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Spam indicators (notebook used #e74c3c)
    axes[0].barh(range(len(spam_words)), spam_scores, color="#e74c3c")
    axes[0].set_yticks(range(len(spam_words)))
    axes[0].set_yticklabels(spam_words)
    axes[0].set_xlabel("Coefficient (Importance)", fontsize=12)
    axes[0].set_title(f"Top {top_n} SPAM indicators", fontsize=14, fontweight="bold")
    axes[0].invert_yaxis()
    axes[0].grid(axis="x", alpha=0.3)

    # Ham indicators (notebook used #2ecc71)
    axes[1].barh(range(len(ham_words)), ham_scores, color="#2ecc71")
    axes[1].set_yticks(range(len(ham_words)))
    axes[1].set_yticklabels(ham_words)
    axes[1].set_xlabel("Coefficient (Importance)", fontsize=12)
    axes[1].set_title(f"Top {top_n} HAM indicators", fontsize=14, fontweight="bold")
    axes[1].invert_yaxis()
    axes[1].grid(axis="x", alpha=0.3)

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "feature_importance.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return fig