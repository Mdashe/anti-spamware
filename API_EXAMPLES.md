# API Usage Examples

This document provides practical examples for using the Spam Classifier API.

## Starting the API Server

```bash
python src/api.py
```

The server will start on `http://localhost:5000`

## Example Requests

### 1. Health Check

**Request:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "spam-classifier-api"
}
```

---

### 2. Get API Information

**Request:**
```bash
curl http://localhost:5000/
```

**Response:**
```json
{
  "service": "Spam Classifier API",
  "version": "1.0.0",
  "endpoints": {
    "GET /": "API information",
    "GET /health": "Health check",
    "POST /predict": "Classify a single message",
    "POST /predict/batch": "Classify multiple messages"
  }
}
```

---

### 3. Classify a Single Message

#### Example 1: Spam Message

**Request:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Congratulations! You won R10,000! Call 073 456 7890 NOW!"
  }'
```

**Response:**
```json
{
  "message": "Congratulations! You won R10,000! Call 073 456 7890 NOW!",
  "prediction": "spam",
  "probabilities": {
    "ham": 0.0001,
    "spam": 0.9999
  }
}
```

#### Example 2: Legitimate Message

**Request:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Your Takealot order has been shipped. Expected delivery: 3-5 days."
  }'
```

**Response:**
```json
{
  "message": "Your Takealot order has been shipped. Expected delivery: 3-5 days.",
  "prediction": "ham",
  "probabilities": {
    "ham": 0.9998,
    "spam": 0.0002
  }
}
```

---

### 4. Batch Classification

**Request:**
```bash
curl -X POST http://localhost:5000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      "URGENT: Claim your R50,000 prize now!",
      "Meeting tomorrow at 2pm in boardroom",
      "Make money from home! WhatsApp 082 123 4567",
      "Your municipal bill is ready for download",
      "100% GUARANTEED FOREX RETURNS!!!"
    ]
  }'
```

**Response:**
```json
{
  "predictions": [
    {
      "message": "URGENT: Claim your R50,000 prize now!",
      "prediction": "spam"
    },
    {
      "message": "Meeting tomorrow at 2pm in boardroom",
      "prediction": "ham"
    },
    {
      "message": "Make money from home! WhatsApp 082 123 4567",
      "prediction": "spam"
    },
    {
      "message": "Your municipal bill is ready for download",
      "prediction": "ham"
    },
    {
      "message": "100% GUARANTEED FOREX RETURNS!!!",
      "prediction": "spam"
    }
  ],
  "count": 5
}
```

---

## Python Client Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:5000"

def classify_message(message):
    """Classify a single message"""
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"message": message}
    )
    return response.json()

def classify_batch(messages):
    """Classify multiple messages"""
    response = requests.post(
        f"{BASE_URL}/predict/batch",
        json={"messages": messages}
    )
    return response.json()

# Example usage
if __name__ == "__main__":
    # Single prediction
    result = classify_message("Win R10,000 today!")
    print(f"Prediction: {result['prediction']}")
    print(f"Spam probability: {result['probabilities']['spam']:.2%}")
    
    # Batch prediction
    messages = [
        "Your order has shipped",
        "Claim your free prize now!",
        "Meeting at 3pm"
    ]
    results = classify_batch(messages)
    for pred in results['predictions']:
        print(f"{pred['message']}: {pred['prediction']}")
```

---

## JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5000';

async function classifyMessage(message) {
  try {
    const response = await axios.post(`${BASE_URL}/predict`, {
      message: message
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  }
}

async function classifyBatch(messages) {
  try {
    const response = await axios.post(`${BASE_URL}/predict/batch`, {
      messages: messages
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  }
}

// Example usage
(async () => {
  // Single prediction
  const result = await classifyMessage('Win R10,000 today!');
  console.log(`Prediction: ${result.prediction}`);
  console.log(`Spam probability: ${(result.probabilities.spam * 100).toFixed(2)}%`);
  
  // Batch prediction
  const messages = [
    'Your order has shipped',
    'Claim your free prize now!',
    'Meeting at 3pm'
  ];
  const results = await classifyBatch(messages);
  results.predictions.forEach(pred => {
    console.log(`${pred.message}: ${pred.prediction}`);
  });
})();
```

---

## Error Handling

### Missing Message Field

**Request:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response (400 Bad Request):**
```json
{
  "error": "Missing required field: message"
}
```

### Empty Message

**Request:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"message": ""}'
```

**Response (400 Bad Request):**
```json
{
  "error": "Message cannot be empty"
}
```

---

## Rate Limiting Considerations

For production deployment:

1. Implement rate limiting (e.g., 100 requests per minute per IP)
2. Add authentication (API keys or OAuth)
3. Use HTTPS for secure communication
4. Monitor API usage and performance
5. Implement caching for frequently requested messages

---

## Testing with curl

Save test messages to a file:

```bash
# test_messages.json
{
  "messages": [
    "Your package has been delivered",
    "WIN R1000000 NOW!!!",
    "Reminder: Team meeting at 10am"
  ]
}
```

Then test:

```bash
curl -X POST http://localhost:5000/predict/batch \
  -H "Content-Type: application/json" \
  -d @test_messages.json
```
