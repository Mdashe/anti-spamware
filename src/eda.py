"""Exploratory data analysis utilities for the spam classifier pipeline.

This module provides dataset quality checks and EDA figure generation
for the spam classification project. It is intended to help detect
missing values, duplicates, class imbalance, and basic text-length
statistics before training.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import string
from nltk.corpus import stopwords

FIGURES_DIR = 'reports/figures'


def _ensure_dirs() -> None:
    """Create output directories required for saving EDA figures."""
    os.makedirs(FIGURES_DIR, exist_ok=True)


def check_data_quality(df: pd.DataFrame) -> dict:
    """Validate dataset quality and return a summary report.

    Parameters
    ----------
    df : pandas.DataFrame
        The input dataset containing at least the columns 'label', 'subject',
        and 'body'.

    Returns
    -------
    dict
        A report summarizing shape, missing values, duplicate rows, class
        distribution, and text length statistics.

    Raises
    ------
    ValueError
        If any rows are missing labels, since training cannot proceed without
        a target value.
    """
    report = {}

    # ── shape ───────────────────────────────────────────────
    report['total_rows']    = len(df)
    report['total_columns'] = len(df.columns)
    report['columns']       = list(df.columns)

    # ── missing values (your notebook Section 2) ────────────
    missing       = df.isnull().sum()
    missing_pct   = (missing / len(df) * 100).round(2)
    report['missing_counts'] = missing.to_dict()
    report['missing_pct']    = missing_pct.to_dict()

    # Hard stop: if the label column has ANY nulls, abort
    if df['label'].isnull().sum() > 0:
        raise ValueError(
            f"label column has {df['label'].isnull().sum()} null values — ",
            "cannot train without labels."
        )

    # ── duplicate rows ───────────────────────────────────────
    n_dupes = df.duplicated(subset = ['subject', 'body']).sum()
    report['duplicate_rows'] = int(n_dupes)
    report['duplicate_rows_pct'] = round(n_dupes / len(df) * 100, 2)
    if n_dupes > 0:
        print(f'WARNING: {n_dupes:,} duplicate rows found ({report["duplicate_rows_pct"]}%). '
              f'Dropping them before training.')
        df = df.drop_duplicates(subset=['subject', 'body']).reset_index(drop=True)

    # ── class distribution (your notebook Section 3) ────────
    class_counts = df['label'].value_counts()
    class_pct    = df['label'].value_counts(normalize=True) * 100
    report['class_counts'] = class_counts.to_dict()
    report['class_pct']    = class_pct.round(2).to_dict()

    # Hard stop: if imbalance is extreme (>20:1), warn loudly
    spam_count = class_counts.get('spam', 0)
    ham_count  = class_counts.get('ham',  1)
    ratio      = spam_count / ham_count
    report['imbalance_ratio'] = round(ratio, 3)
    if ratio > 20 or ratio < 0.05:
        print(f'WARNING: severe class imbalance detected (ratio={ratio:.2f}). '
              f'Consider oversampling or class weights.')

    # ── text length stats (your notebook Section 3) ─────────

    df['full_text']   = df['subject'].fillna('') + ' ' + df['body'].fillna('')
    df['text_length'] = df['full_text'].str.len()
    df['word_count']  = df['full_text'].str.split().str.len()
    length_stats = df.groupby('label')[['text_length','word_count']].describe()
    report['length_stats'] = length_stats.to_dict()

    return report, df


def plot_eda(df: pd.DataFrame) -> None:
    """Generate and save exploratory data analysis figures.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataset containing at least the columns 'label', 'subject', and
        'body' required to generate distribution and missing-value plots.

    Notes
    -----
    This function writes PNG files to the configured figures directory and is
    intended to run during pipeline setup rather than on every training run.
    """
    _ensure_dirs()

    # ── 1. class distribution ────────────────────────────────
    class_counts = df['label'].value_counts()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.countplot(data=df, x='label', hue='label',
              palette={'ham':'#1D9E75', 'spam':'#E24B4A'},
              legend=False, ax=axes[0])
    for c in axes[0].containers: axes[0].bar_label(c, fmt='%d')
    axes[0].set_title('Class distribution — count')
    axes[1].pie(class_counts, labels=class_counts.index,
                autopct='%1.1f%%',
                colors=['#1D9E75','#E24B4A'], startangle=90)
    axes[1].set_title('Class distribution — percentage')
    fig.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/eda_class_distribution.png', dpi=150)
    plt.close(fig)

    # ── 2. text length & word count distributions ────────────
    df = df.copy()
    df['full_text']   = df['subject'].fillna('') + ' ' + df['body'].fillna('')
    df['text_length'] = df['full_text'].str.len()
    df['word_count']  = df['full_text'].str.split().str.len()
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    for label, colour in [('ham','#1D9E75'),('spam','#E24B4A')]:
        axes[0,0].hist(df[df['label']==label]['text_length'],
                       bins=50, alpha=0.6, label=label, color=colour)
        axes[0,1].hist(df[df['label']==label]['word_count'],
                       bins=50, alpha=0.6, label=label, color=colour)
    axes[0,0].set_title('Character length distribution')
    axes[0,0].legend()
    axes[0,1].set_title('Word count distribution')
    axes[0,1].legend()
    df.boxplot(column='text_length', by='label', ax=axes[1,0], grid=False)
    df.boxplot(column='word_count',  by='label', ax=axes[1,1], grid=False)
    axes[1,0].set_title('Character length by class')
    axes[1,1].set_title('Word count by class')
    fig.suptitle('')
    fig.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/eda_text_length_distributions.png', dpi=150)
    plt.close(fig)

    # ── 3. missing values heatmap ────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    missing_pct = df.isnull().mean() * 100
    missing_pct.plot(kind='bar', ax=ax, color='#2E75B6')
    ax.set_title('Missing values per column (%)')
    ax.set_ylabel('% missing')
    ax.set_ylim(0, 100)
    for bar in ax.patches:
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.5,
                f'{bar.get_height():.1f}%',
                ha='center', va='bottom', fontsize=9)
    fig.tight_layout()
    fig.savefig(f'{FIGURES_DIR}/eda_missing_values.png', dpi=150)
    plt.close(fig)

    print(f'EDA figures saved to {FIGURES_DIR}/')
