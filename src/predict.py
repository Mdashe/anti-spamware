"""
Interactive prediction script for spam classifier.

This module loads a trained spam classification model and TF-IDF vectorizer,
then exposes a command-line interface for single-message classification.
It also supports probability output for confidence reporting.
"""

import pickle
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))
from preprocess import TextPreprocessor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SpamPredictor:
    """Spam prediction interface using trained model."""
    
    def __init__(self, model_path, vectorizer_path):
        """
        Initialize predictor with trained model and vectorizer.
        
        Args:
            model_path: Path to trained model pickle file
            vectorizer_path: Path to TF-IDF vectorizer pickle file
        """
        self.preprocessor = TextPreprocessor()
        self.model = self._load_model(model_path)
        self.vectorizer = self._load_vectorizer(vectorizer_path)
    
    def _load_model(self, model_path):
        """Load trained model from pickle file."""
        logger.info(f"Loading model from {model_path}")
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model
    
    def _load_vectorizer(self, vectorizer_path):
        """Load TF-IDF vectorizer from pickle file."""
        logger.info(f"Loading vectorizer from {vectorizer_path}")
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        return vectorizer
    
    def predict(self, message, return_proba=False):
        """
        Predict if a message is spam or ham.
        
        Args:
            message: Text message to classify
            return_proba: If True, return probability scores
        
        Returns:
            Prediction ('spam' or 'ham') and optionally probability scores
        """
        # Preprocess the message
        processed_message = self.preprocessor.preprocess(message)
        
        # Vectorize
        message_tfidf = self.vectorizer.transform([processed_message])
        
        # Predict
        prediction = self.model.predict(message_tfidf)[0]
        label = 'spam' if prediction == 1 else 'ham'
        
        if return_proba:
            probabilities = self.model.predict_proba(message_tfidf)[0]
            return label, {
                'ham_probability': probabilities[0],
                'spam_probability': probabilities[1]
            }
        
        return label
    
    def predict_batch(self, messages):
        """
        Predict multiple messages at once.
        
        Args:
            messages: List of text messages to classify
        
        Returns:
            List of predictions
        """
        # Preprocess all messages
        processed_messages = [self.preprocessor.preprocess(msg) for msg in messages]
        
        # Vectorize
        messages_tfidf = self.vectorizer.transform(processed_messages)
        
        # Predict
        predictions = self.model.predict(messages_tfidf)
        
        # Convert to labels
        labels = ['spam' if pred == 1 else 'ham' for pred in predictions]
        
        return labels


def main():
    """Interactive prediction interface."""
    # Define paths
    project_root = Path(__file__).parent.parent
    model_path = project_root / 'models' / 'model.pkl'
    vectorizer_path = project_root / 'models' / 'vectorizer.pkl'
    
    # Check if model exists
    if not model_path.exists() or not vectorizer_path.exists():
        logger.error("Model files not found. Please run train.py first.")
        return
    
    # Initialize predictor
    predictor = SpamPredictor(model_path, vectorizer_path)
    
    print("\n" + "="*60)
    print("SPAM CLASSIFIER - Interactive Prediction")
    print("="*60)
    print("\nEnter a message to classify (or 'quit' to exit)")
    print("-"*60 + "\n")
    
    while True:
        try:
            # Get user input
            message = input("Message: ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not message:
                print("Please enter a message.\n")
                continue
            
            # Make prediction
            label, probabilities = predictor.predict(message, return_proba=True)
            
            # Display results
            print(f"\nPrediction: {label.upper()}")
            print(f"Confidence:")
            print(f"  - Ham:  {probabilities['ham_probability']*100:.2f}%")
            print(f"  - Spam: {probabilities['spam_probability']*100:.2f}%")
            print("-"*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
