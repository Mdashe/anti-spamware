"""
Flask API for spam classifier.
Provides REST endpoints for spam detection.
"""

from flask import Flask, request, jsonify
from pathlib import Path
import sys
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))
from predict import SpamPredictor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize predictor (will be loaded on first request)
predictor = None


def get_predictor():
    """Get or initialize the SpamPredictor instance.

    This function lazily initializes the predictor the first time the API
    receives a request. On subsequent calls, the same instance is reused
    to avoid reloading the model and vectorizer repeatedly.
    """
    global predictor
    if predictor is None:
        project_root = Path(__file__).parent.parent
        model_path = project_root / 'models' / 'model.pkl'
        vectorizer_path = project_root / 'models' / 'vectorizer.pkl'
        
        logger.info("Loading spam classifier model")
        predictor = SpamPredictor(model_path, vectorizer_path)
        logger.info("Model loaded successfully")
    
    return predictor


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'spam-classifier-api'
    }), 200


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict if a message is spam or ham.
    
    Request body:
        {
            "message": "Your message text here"
        }
    
    Response:
        {
            "message": "original message",
            "prediction": "spam" or "ham",
            "probabilities": {
                "ham": 0.123,
                "spam": 0.877
            }
        }
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate input
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing required field: message'
            }), 400
        
        message = data['message']
        
        if not message or not message.strip():
            return jsonify({
                'error': 'Message cannot be empty'
            }), 400
        
        # Get predictor
        pred = get_predictor()
        
        # Make prediction
        label, probabilities = pred.predict(message, return_proba=True)
        
        # Return response
        return jsonify({
            'message': message,
            'prediction': label,
            'probabilities': {
                'ham': round(probabilities['ham_probability'], 4),
                'spam': round(probabilities['spam_probability'], 4)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Predict multiple messages at once.
    
    Request body:
        {
            "messages": ["message 1", "message 2", ...]
        }
    
    Response:
        {
            "predictions": [
                {
                    "message": "message 1",
                    "prediction": "spam"
                },
                ...
            ]
        }
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate input
        if not data or 'messages' not in data:
            return jsonify({
                'error': 'Missing required field: messages'
            }), 400
        
        messages = data['messages']
        
        if not isinstance(messages, list):
            return jsonify({
                'error': 'messages must be a list'
            }), 400
        
        if not messages:
            return jsonify({
                'error': 'messages list cannot be empty'
            }), 400
        
        # Get predictor
        pred = get_predictor()
        
        # Make predictions
        labels = pred.predict_batch(messages)
        
        # Format response
        results = [
            {
                'message': msg,
                'prediction': label
            }
            for msg, label in zip(messages, labels)
        ]
        
        return jsonify({
            'predictions': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error during batch prediction: {e}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/', methods=['GET'])
def index():
    """API information endpoint."""
    return jsonify({
        'service': 'Spam Classifier API',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'POST /predict': 'Classify a single message',
            'POST /predict/batch': 'Classify multiple messages'
        },
        'example_request': {
            'url': '/predict',
            'method': 'POST',
            'body': {
                'message': 'Congratulations! You won R10,000!'
            }
        }
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
