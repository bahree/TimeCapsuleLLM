#!/bin/bash

echo "🏛️  London Historical LLM - Remote Machine Setup"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Please run this script from the TimeCapsuleLLM directory"
    exit 1
fi

# Check Python environment
echo "🐍 Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "london-llm-env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv london-llm-env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source london-llm-env/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install PyTorch with CUDA (if available)
if command -v nvidia-smi &> /dev/null; then
    echo "🚀 Installing PyTorch with CUDA support..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    echo "💻 Installing PyTorch CPU version..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Check if data exists
if [ ! -f "data/london_data/london_corpus_merged.txt" ]; then
    echo "📥 Data not found. Running data preparation..."
    python data_preparation_fixed.py
fi

# Check if tokenizer exists
if [ ! -d "tokenizer_london" ]; then
    echo "🔤 Training tokenizer..."
    python train_tokenizer_london.py
fi

# Check if dataset binaries exist
if [ ! -f "data/london_data/train.bin" ]; then
    echo "📦 Preparing dataset..."
    python prepare_dataset.py
fi

# Make scripts executable
chmod +x launch_2gpu.sh
chmod +x launch_2gpu.bat

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start training:"
echo "   Single GPU: python train_london_llm_simple.py"
echo "   Multi GPU:  ./launch_2gpu.sh"
echo ""
echo "📊 To monitor training:"
echo "   watch -n 1 nvidia-smi"
echo ""
echo "🎉 Ready to train your London Historical LLM!"
