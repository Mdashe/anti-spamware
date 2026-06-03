"""
Unit tests for spam classifier.
Tests preprocessing, training, and prediction functionality.
"""

import unittest
import sys
from pathlib import Path
import pandas as pd
import tempfile
import pickle

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from preprocess import TextPreprocessor
from predict import SpamPredictor


class TestTextPreprocessor(unittest.TestCase):
    """Test cases for TextPreprocessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.preprocessor = TextPreprocessor()
    
    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        text = "Hello World! This is a TEST."
        result = self.preprocessor.clean_text(text)
        expected = "hello world this is a test"
        self.assertEqual(result, expected)
    
    def test_clean_text_urls(self):
        """Test URL removal."""
        text = "Visit http://example.com or www.example.com"
        result = self.preprocessor.clean_text(text)
        self.assertNotIn("http", result)
        self.assertNotIn("www", result)
    
    def test_clean_text_phone_numbers(self):
        """Test phone number removal."""
        text = "Call me at 073 456 7890 or +27734567890"
        result = self.preprocessor.clean_text(text)
        # Should not contain the phone number
        self.assertNotIn("073", result)
        self.assertNotIn("+27", result)
    
    def test_clean_text_currency(self):
        """Test currency amount removal."""
        text = "Win R10,000 or R5000 today!"
        result = self.preprocessor.clean_text(text)
        # Should not contain currency amounts
        self.assertNotIn("10000", result)
        self.assertNotIn("5000", result)
    
    def test_remove_stop_words(self):
        """Test stop word removal."""
        text = "the cat is on the mat"
        result = self.preprocessor.remove_stop_words(text)
        self.assertNotIn("the", result)
        self.assertNotIn("is", result)
        self.assertNotIn("on", result)
        self.assertIn("cat", result)
        self.assertIn("mat", result)
    
    def test_preprocess_pipeline(self):
        """Test full preprocessing pipeline."""
        text = "CONGRATULATIONS! You won R10,000! Call 073 456 7890 NOW!!!"
        result = self.preprocessor.preprocess(text)
        # Should be cleaned and lowercased
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        # Should not contain original formatting
        self.assertNotIn("CONGRATULATIONS", result)
        self.assertNotIn("!!!", result)
    
    def test_preprocess_empty_string(self):
        """Test preprocessing empty string."""
        result = self.preprocessor.preprocess("")
        self.assertEqual(result, "")
    
    def test_preprocess_none(self):
        """Test preprocessing None value."""
        result = self.preprocessor.preprocess(None)
        self.assertEqual(result, "")


class TestSpamPredictorMock(unittest.TestCase):
    """Test cases for SpamPredictor class with mock model."""
    
    def setUp(self):
        """Set up test fixtures with temporary model files."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.model_path = Path(self.temp_dir) / 'model.pkl'
        self.vectorizer_path = Path(self.temp_dir) / 'vectorizer.pkl'
        
        # Create mock model (simple majority classifier)
        class MockModel:
            def predict(self, X):
                # Always predict spam (1)
                return [1] * X.shape[0]
            
            def predict_proba(self, X):
                # Return [ham_prob, spam_prob] for each sample
                return [[0.2, 0.8] for _ in range(X.shape[0])]
        
        # Create mock vectorizer
        from sklearn.feature_extraction.text import TfidfVectorizer
        mock_vectorizer = TfidfVectorizer(max_features=10)
        # Fit on sample data
        mock_vectorizer.fit(['spam message', 'ham message', 'test message'])
        
        # Save mock model and vectorizer
        with open(self.model_path, 'wb') as f:
            pickle.dump(MockModel(), f)
        
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(mock_vectorizer, f)
    
    def test_predictor_initialization(self):
        """Test predictor initialization."""
        predictor = SpamPredictor(self.model_path, self.vectorizer_path)
        self.assertIsNotNone(predictor.model)
        self.assertIsNotNone(predictor.vectorizer)
        self.assertIsNotNone(predictor.preprocessor)
    
    def test_predict_single_message(self):
        """Test prediction on single message."""
        predictor = SpamPredictor(self.model_path, self.vectorizer_path)
        message = "Congratulations! You won R10,000!"
        label = predictor.predict(message)
        self.assertIn(label, ['spam', 'ham'])
    
    def test_predict_with_probabilities(self):
        """Test prediction with probabilities."""
        predictor = SpamPredictor(self.model_path, self.vectorizer_path)
        message = "Congratulations! You won R10,000!"
        label, probabilities = predictor.predict(message, return_proba=True)
        
        self.assertIn(label, ['spam', 'ham'])
        self.assertIn('ham_probability', probabilities)
        self.assertIn('spam_probability', probabilities)
        self.assertAlmostEqual(
            probabilities['ham_probability'] + probabilities['spam_probability'], 
            1.0, 
            places=5
        )
    
    def test_predict_batch(self):
        """Test batch prediction."""
        predictor = SpamPredictor(self.model_path, self.vectorizer_path)
        messages = [
            "Congratulations! You won R10,000!",
            "Your order has been shipped",
            "Call now for a free loan"
        ]
        labels = predictor.predict_batch(messages)
        
        self.assertEqual(len(labels), len(messages))
        for label in labels:
            self.assertIn(label, ['spam', 'ham'])
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)


class TestDataPreprocessing(unittest.TestCase):
    """Test cases for data preprocessing functions."""
    
    def test_sample_spam_messages(self):
        """Test preprocessing on sample spam messages."""
        preprocessor = TextPreprocessor()
        
        spam_samples = [
            "CONGRATULATIONS! You won R10,000! Call 073 456 7890",
            "Make R50,000 daily from home! WhatsApp 082 123 4567",
            "Sangoma love spells - 100% guaranteed. Call Mama Zodwa"
        ]
        
        for message in spam_samples:
            processed = preprocessor.preprocess(message)
            # Should not be empty
            self.assertTrue(len(processed) > 0)
            # Should be lowercase
            self.assertEqual(processed, processed.lower())
    
    def test_sample_ham_messages(self):
        """Test preprocessing on sample ham messages."""
        preprocessor = TextPreprocessor()
        
        ham_samples = [
            "Your order has been shipped. Track at www.example.com",
            "Meeting scheduled for tomorrow at 3pm",
            "Thank you for your purchase. Order #12345"
        ]
        
        for message in ham_samples:
            processed = preprocessor.preprocess(message)
            # Should not be empty
            self.assertTrue(len(processed) > 0)
            # Should be lowercase
            self.assertEqual(processed, processed.lower())


def run_tests():
    """Run all tests and display results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestTextPreprocessor))
    suite.addTests(loader.loadTestsFromTestCase(TestSpamPredictorMock))
    suite.addTests(loader.loadTestsFromTestCase(TestDataPreprocessing))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
