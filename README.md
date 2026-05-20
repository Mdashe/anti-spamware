# Spam Email Classifier 🇿🇦

A machine learning-powered spam email classifier specifically trained on South African spam patterns. This project includes data preprocessing, model training, evaluation, and a REST API for real-time predictions.

## Project Overview

This spam classifier uses Natural Language Processing (NLP) and Machine Learning to identify spam emails. The model is trained on a dataset of 100,000 South African emails containing local spam patterns such as:

- Sangoma/traditional healer scams
- Forex trading schemes  
- Work-from-home opportunities
- Government grant scams
- Cash loan offers
- Male enhancement products
- Lottery/prize scams

## Project Structure

```
spam-classifier/
├── data/
│   ├── raw/              # Original dataset
│   │   └── spam.csv
│   └── processed/        # Cleaned and preprocessed data
│       └── spam_processed.csv
├── notebooks/
│   └── eda.ipynb        # Exploratory Data Analysis
├── src/
│   ├── preprocess.py    # Data preprocessing pipeline
│   ├── train.py         # Model training script
│   ├── predict.py       # Prediction interface
│   └── api.py          # Flask REST API
├── models/
│   ├── vectorizer.pkl   # TF-IDF vectorizer
│   └── model.pkl       # Trained classifier
├── tests/
│   └── test_model.py   # Unit tests
├── Dockerfile          # Docker configuration
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

##  Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

1. **Clone the repository** (or extract the project files)

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Preprocess the data:**
   ```bash
   python src/preprocess.py
   ```
   This will:
   - Load the raw dataset
   - Clean and normalize text
   - Remove URLs, phone numbers, and currency amounts
   - Save processed data to `data/processed/`

4. **Train the model:**
   ```bash
   python src/train.py
   ```
   This will:
   - Load preprocessed data
   - Split into train/test sets (80/20)
   - Train a Naive Bayes classifier with TF-IDF features
   - Evaluate performance
   - Save model to `models/`

##  Model Performance

The classifier achieves:
- **High accuracy** on the test set
- **Low false positive rate** (legitimate emails correctly classified)
- **High spam detection rate** (spam emails correctly identified)

Detailed metrics are displayed after training.

## Usage

### Interactive Prediction

Run the interactive prediction interface:

```bash
python src/predict.py
```

Then enter messages to classify:

```
Message: Congratulations! You won R10,000! Call now!
Prediction: SPAM
Confidence:
  - Ham:  5.23%
  - Spam: 94.77%
```

### REST API

Start the Flask API server:

```bash
python src/api.py
```

The API will be available at `http://localhost:5000`

#### API Endpoints

**1. Health Check**
```bash
curl http://localhost:5000/health
```

**2. Predict Single Message**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"message": "Congratulations! You won R10,000!"}'
```

Response:
```json
{
  "message": "Congratulations! You won R10,000!",
  "prediction": "spam",
  "probabilities": {
    "ham": 0.0523,
    "spam": 0.9477
  }
}
```

**3. Predict Multiple Messages**
```bash
curl -X POST http://localhost:5000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      "Your order has been shipped",
      "Win R50,000 today! Call now!"
    ]
  }'
```

Response:
```json
{
  "predictions": [
    {
      "message": "Your order has been shipped",
      "prediction": "ham"
    },
    {
      "message": "Win R50,000 today! Call now!",
      "prediction": "spam"
    }
  ],
  "count": 2
}
```

##  Docker Deployment

Build the Docker image:

```bash
docker build -t spam-classifier .
```

Run the container:

```bash
docker run -p 5000:5000 spam-classifier
```

The API will be accessible at `http://localhost:5000`

##  Running Tests

Execute the unit tests:

```bash
python tests/test_model.py
```

This will test:
- Text preprocessing functions
- Model prediction capabilities
- API functionality

## Exploratory Data Analysis

Open the Jupyter notebook to explore the dataset:

```bash
jupyter notebook notebooks/eda.ipynb
```

The notebook includes:
- Dataset overview and statistics
- Label distribution analysis
- Text length analysis
- Common words and n-grams
- Word clouds
- Pattern analysis (URLs, phone numbers, money amounts, etc.)

## Customization

### Adjusting Model Parameters

Edit `src/train.py` to modify:
- `max_features`: Number of TF-IDF features (default: 5000)
- `ngram_range`: N-gram range for feature extraction (default: (1,2))
- `test_size`: Train/test split ratio (default: 0.2)
- `alpha`: Smoothing parameter for Naive Bayes (default: 0.1)

### Adding New Features

You can enhance the preprocessor in `src/preprocess.py` to:
- Add domain-specific stop words
- Include additional pattern detection
- Implement stemming or lemmatization
- Extract custom features

##  Dataset Information

- **Size:** 100,000 emails
- **Features:** 
  - `email_id`: Unique identifier
  - `subject`: Email subject line
  - `body`: Email body content
  - `label`: Classification (spam/ham)

- **Distribution:** 
  - Spam messages: ~70%
  - Ham messages: ~30%

##  Security Considerations

- API should be deployed behind authentication in production
- Consider rate limiting for the prediction endpoints
- Sanitize user inputs to prevent injection attacks
- Use HTTPS in production environments

##  Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

##  License

This project is provided for educational and research purposes.

##  Acknowledgments

- Dataset created specifically for South African spam patterns
- Built with scikit-learn and Flask
- Inspired by real-world spam detection challenges

## Support

For questions or issues:
- Check the documentation in this README
- Review the code comments
- Run the test suite to verify functionality

---

**Built with  for spam-free inboxes**
