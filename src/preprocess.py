"""
Preprocessing utilities for the South African spam classifier.

This module defines a reusable text preprocessing pipeline that:
- loads and cleans raw email text,
- removes common English stop words using NLTK,
- combines subject and body fields,
- encodes labels for model training,
- and saves cleaned output to CSV.

The pipeline is designed to support model training and evaluation workflows
by producing a stable `processed_text` feature column.
"""

import pandas as pd
import re
import string
from pathlib import Path
import logging

import nltk
from nltk.corpus import stopwords

# Setup logging configuration for module-level diagnostics
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TextPreprocessor:
    """Handle text preprocessing for spam classification.

    This class encapsulates cleaning, normalization, and stop-word removal.
    It is intentionally lightweight and deterministic so that preprocessing can
    be reproduced consistently across training and inference.
    """
    
    def __init__(self):
        # Load the standard English stop word list from NLTK once per instance.
        self.stop_words = self._load_stop_words()
    
    def _load_stop_words(self):
        """Load English stop words from the NLTK corpus.

        If the stopwords corpus is not installed, download it automatically.
        This avoids failing when the code is first executed in a fresh
        environment.
        """
        try:
            return set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords', quiet=True)
            return set(stopwords.words('english'))
    
    def clean_text(self, text):
        """Clean and normalize raw email text.

        Steps:
        1. Normalize missing values to an empty string.
        2. Convert all characters to lowercase.
        3. Remove URLs, email addresses, phone numbers, and currency amounts.
        4. Strip punctuation and collapse duplicate whitespace.
        """
        if pd.isna(text):
            return ""
        
        # Normalize text to lowercase for case-insensitive processing.
        text = str(text).lower()
        
        # Remove URLs and web links commonly found in spam messages.
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove email addresses to avoid leaking specific contact info.
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove South African phone numbers and common phone formats.
        text = re.sub(r'(\+27|0)\d{9,10}|\d{3}\s?\d{3}\s?\d{4}', '', text)
        
        # Remove currency amounts such as R1000 or R1,234.56.
        text = re.sub(r'r\s?\d+[,\d]*\.?\d*', '', text)
        
        # Remove punctuation to simplify tokenization.
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Collapse multiple spaces and trim leading/trailing whitespace.
        text = ' '.join(text.split())
        
        return text
    
    def remove_stop_words(self, text):
        """Remove English stop words from cleaned text.

        Stop words are removed after cleaning so punctuation and casing do not
        affect the stop word filtering.
        """
        words = text.split()
        filtered_words = [word for word in words if word not in self.stop_words]
        return ' '.join(filtered_words)
    
    def preprocess(self, text):
        """Run the full preprocessing pipeline on a single text input."""
        text = self.clean_text(text)
        text = self.remove_stop_words(text)
        return text


def load_data(data_path):
    """Load the raw spam dataset from disk.

    Args:
        data_path (Path or str): Path to the CSV file containing raw spam data.

    Returns:
        pandas.DataFrame: Raw dataset with columns such as subject, body, and label.
    """
    logger.info(f"Loading data from {data_path}")
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} records")
    return df


def preprocess_data(df):
    """Preprocess the full dataset.

    This function combines email subject and body fields, runs text cleaning,
    removes stop words, encodes labels, and drops any rows with empty processed
    text. It also logs summary statistics for spam and ham proportions.

    Args:
        df (pandas.DataFrame): Raw dataset containing 'subject', 'body', and 'label'.

    Returns:
        pandas.DataFrame: Dataset augmented with 'text', 'processed_text',
        'is_duplicate', and 'label_encoded'.
    """
    logger.info("Starting data preprocessing")
    
    # Initialize preprocessor
    preprocessor = TextPreprocessor()
    
    # Combine subject and body text into a single column for processing.
    logger.info("Combining subject and body text")
    df['text'] = df['subject'].fillna('') + ' ' + df['body'].fillna('')
    
    # Preprocess text and create a cleaned text column.
    logger.info("Cleaning and preprocessing text")
    df['processed_text'] = df['text'].apply(preprocessor.preprocess)
    
    # Flag duplicate records based on normalized processed text.
    # All rows sharing the same cleaned text are marked True.
    logger.info("Flagging duplicate messages")
    df['is_duplicate'] = df.duplicated(subset=['processed_text'], keep=False)
    
    # Convert labels to binary numeric values, where spam=1 and ham=0.
    logger.info("Encoding labels")
    df['label_encoded'] = (df['label'] == 'spam').astype(int)
    
    # Discard any rows where the cleaned text is empty.
    df = df[df['processed_text'].str.len() > 0].copy()
    logger.info(f"Remaining records after cleaning: {len(df)}")
    
    # Basic class distribution logging.
    spam_count = (df['label_encoded'] == 1).sum()
    ham_count = (df['label_encoded'] == 0).sum()
    logger.info(f"Spam messages: {spam_count} ({spam_count/len(df)*100:.2f}%)")
    logger.info(f"Ham messages: {ham_count} ({ham_count/len(df)*100:.2f}%)")
    
    return df


def save_processed_data(df, output_path):
    """Save the processed dataset to a CSV file.

    Args:
        df (pandas.DataFrame): Dataset containing processed text and encoded labels.
        output_path (Path or str): Destination path for the output CSV file.
    """
    logger.info(f"Saving processed data to {output_path}")
    
    # Keep only the columns needed for downstream training/evaluation.
    processed_df = df[['email_id', 'text', 'processed_text', 'label', 'label_encoded', 'is_duplicate']]
    
    # Write the cleaned dataset to disk.
    processed_df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(processed_df)} records")


def main():
    """Run the end-to-end preprocessing pipeline.

    This function locates the raw data file, preprocesses the dataset, ensures
    the output directory exists, and writes the cleaned CSV file.
    """
    # Define paths
    project_root = Path(__file__).parent.parent
    raw_data_path = project_root / 'data' / 'raw' / 'spam.csv'
    processed_data_path = project_root / 'data' / 'processed' / 'spam_processed.csv'
    
    # Create output directory if it doesn't already exist.
    processed_data_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load raw dataset.
    df = load_data(raw_data_path)
    
    # Run preprocessing on the loaded dataset.
    df = preprocess_data(df)
    
    # Save the cleaned dataset.
    save_processed_data(df, processed_data_path)
    
    logger.info("Preprocessing complete!")


if __name__ == "__main__":
    main()
