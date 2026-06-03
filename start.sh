#!/bin/bash

# Spam Classifier Quick Start Script
# This script sets up and runs the spam classifier project

echo "======================================"
echo "Spam Classifier Setup"
echo "======================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check if models exist
if [ ! -f "models/model.pkl" ] || [ ! -f "models/vectorizer.pkl" ]; then
    echo ""
    echo "Models not found. Running training pipeline..."
    echo ""
    
    # Preprocess data
    echo "Step 1/2: Preprocessing data..."
    python src/preprocess.py
    
    # Train model
    echo ""
    echo "Step 2/2: Training model..."
    python src/train.py
    
    echo ""
    echo "✓ Training complete!"
else
    echo "✓ Models already trained"
fi

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Choose an option:"
echo "  1) Run interactive prediction"
echo "  2) Start API server"
echo "  3) Run tests"
echo "  4) Open Jupyter notebook (EDA)"
echo "  5) Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "Starting interactive prediction..."
        echo ""
        python src/predict.py
        ;;
    2)
        echo ""
        echo "Starting API server on http://localhost:5000"
        echo "Press Ctrl+C to stop"
        echo ""
        python src/api.py
        ;;
    3)
        echo ""
        echo "Running tests..."
        echo ""
        python tests/test_model.py
        ;;
    4)
        echo ""
        echo "Opening Jupyter notebook..."
        echo ""
        jupyter notebook notebooks/eda.ipynb
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
