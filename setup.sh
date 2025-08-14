#!/bin/bash

echo "🚚 Setting up Supply Chain Optimization Platform..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Generate sample data
echo "📊 Generating sample data..."
python src/data_generation/synthetic_data.py

echo "✅ Setup complete!"
echo ""
echo "🚀 To run the application:"
echo "   Dashboard: streamlit run src/dashboard/streamlit_app.py"
echo "   API: python src/api/main.py"
echo ""
echo "🌐 Access points:"
echo "   Dashboard: http://localhost:8501"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
