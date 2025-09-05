#!/bin/bash
# Quick fix for externally-managed-environment error

echo "🔧 Fixing externally-managed-environment error"
echo "=============================================="

# Check if virtual environment already exists
if [ -d "london-llm-env" ]; then
    echo "⚠️  Virtual environment already exists"
    echo "Activating existing virtual environment..."
    source london-llm-env/bin/activate
else
    echo "📦 Creating virtual environment..."
    python3 -m venv london-llm-env
    
    echo "🔄 Activating virtual environment..."
    source london-llm-env/bin/activate
    
    echo "⬆️  Upgrading pip..."
    pip install --upgrade pip
fi

echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Always activate the virtual environment: source london-llm-env/bin/activate"
echo "2. Run: python test_setup.py"
echo "3. Run: python setup_multi_gpu.py"
echo ""
echo "💡 Remember to activate the virtual environment before running any Python commands!"
