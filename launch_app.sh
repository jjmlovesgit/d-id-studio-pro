#!/bin/bash
cd "$(dirname "$0")"

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "🚀 Launching D-ID Studio Pro..."
python app.py
