    """
Model training script for spam classifier.

This module trains and compares candidate classifiers using TF-IDF features.
It supports Naive Bayes, Logistic Regression, and Linear SVM, then selects the
best model by F1 score and saves both the trained model and the vectorizer.
"""

import pandas as pd
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.metrics import precision_recall_fscore_support
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SpamClassifier:
    """Spam classification model using Naive Bayes."""
    
    def __init__(self, max_features=5000, ngram_range=(1, 2)):
        """
        Initialize the spam classifier.
        
        Args:
            max_features: Maximum number of features for TF-IDF
            ngram_range: Range of n-grams to extract
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            min_df=2,
            max_df=0.95
        )
        self.model = MultinomialNB(alpha=0.1)
        self.is_trained = False
    
    def train(self, X_train, y_train):
        """Train the classifier."""
        logger.info("Training TF-IDF vectorizer")
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        logger.info(f"TF-IDF feature matrix shape: {X_train_tfidf.shape}")
        
        logger.info("Training Naive Bayes model")
        self.model.fit(X_train_tfidf, y_train)
        self.is_trained = True
        logger.info("Model training complete")
    
    def predict(self, X):
        """Make predictions on new data."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_tfidf = self.vectorizer.transform(X)
        return self.model.predict(X_tfidf)
    
    def predict_proba(self, X):
        """Get prediction probabilities."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_tfidf = self.vectorizer.transform(X)
        return self.model.predict_proba(X_tfidf)
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance."""
        logger.info("Evaluating model performance")
        predictions = self.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, predictions, average='binary'
        )
        
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"Precision: {precision:.4f}")
        logger.info(f"Recall: {recall:.4f}")
        logger.info(f"F1-Score: {f1:.4f}")
        
        # Print classification report
        logger.info("\nClassification Report:")
        print(classification_report(
            y_test, predictions, 
            target_names=['Ham', 'Spam']
        ))
        
        # Print confusion matrix
        logger.info("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, predictions)
        print(f"True Negatives (Ham correctly classified): {cm[0][0]}")
        print(f"False Positives (Ham classified as Spam): {cm[0][1]}")
        print(f"False Negatives (Spam classified as Ham): {cm[1][0]}")
        print(f"True Positives (Spam correctly classified): {cm[1][1]}")
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm
        }


def load_processed_data(data_path):
    """Load preprocessed data."""
    logger.info(f"Loading processed data from {data_path}")
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} records")
    return df


def split_data(df, test_size=0.2, random_state=42):
    """Split data into train and test sets."""
    logger.info(f"Splitting data with test size: {test_size}")
    
    X = df['processed_text']
    y = df['label_encoded']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=test_size, 
        random_state=random_state,
        stratify=y
    )
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    return X_train, X_test, y_train, y_test


def build_classifiers():
    """Return a dictionary of classifiers to compare."""
    return {
        'Naive Bayes': MultinomialNB(alpha=0.1),
        'Logistic Regression': LogisticRegression(solver='liblinear', max_iter=1000),
        'Linear SVM': LinearSVC(max_iter=10000)
    }


def evaluate_model(name, model, X_train_tfidf, X_test_tfidf, y_train, y_test):
    """Train and evaluate a single classifier on TF-IDF features."""
    logger.info(f"Training and evaluating {name}")
    model.fit(X_train_tfidf, y_train)
    predictions = model.predict(X_test_tfidf)

    accuracy = accuracy_score(y_test, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, predictions, average='binary'
    )

    logger.info(f"{name} - Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")

    return {
        'name': name,
        'model': model,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'predictions': predictions
    }


def compare_classifiers(X_train, X_test, y_train, y_test):
    """Compare multiple classifiers using the same TF-IDF feature set."""
    logger.info("Preparing TF-IDF features for classifier comparison")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95
    )

    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    results = []
    for name, model in build_classifiers().items():
        result = evaluate_model(name, model, X_train_tfidf, X_test_tfidf, y_train, y_test)
        results.append(result)

    best_result = max(results, key=lambda item: item['f1_score'])
    logger.info(f"Best classifier: {best_result['name']} with F1 score {best_result['f1_score']:.4f}")

    return best_result, vectorizer


def save_model(model, vectorizer, model_path, vectorizer_path):
    """Save trained model and vectorizer."""
    logger.info(f"Saving model to {model_path}")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    logger.info(f"Saving vectorizer to {vectorizer_path}")
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    logger.info("Model and vectorizer saved successfully")


def main():
    """Main training pipeline."""
    # Define paths
    project_root = Path(__file__).parent.parent
    processed_data_path = project_root / 'data' / 'processed' / 'spam_processed.csv'
    model_path = project_root / 'models' / 'model.pkl'
    vectorizer_path = project_root / 'models' / 'vectorizer.pkl'
    
    # Create models directory if it doesn't exist
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load data
    df = load_processed_data(processed_data_path)
    
    # Split data
    X_train, X_test, y_train, y_test = split_data(df)
    
    # Compare candidate classifiers and pick the best model
    best_result, vectorizer = compare_classifiers(X_train, X_test, y_train, y_test)
    
    # Save the best performing model and shared vectorizer
    save_model(best_result['model'], vectorizer, model_path, vectorizer_path)
    
    logger.info("Training pipeline complete!")


if __name__ == "__main__":
    main()
