#!/bin/bash

echo "🚀 Committing and pushing London Historical LLM updates..."
echo "=================================================="

# Add all changes
echo "📁 Adding files..."
git add .

# Commit with descriptive message
echo "💾 Committing changes..."
git commit -m "Add custom historical tokenizer and improved dataset preparation

- Added train_custom_tokenizer.py for 30,000 token vocabulary
- Updated prepare_dataset.py to use custom tokenizer
- Added setup_with_custom_tokenizer.py for complete setup
- Custom tokenizer optimized for 1500-1850 historical English
- Special tokens for years, dates, names, places
- Much better text generation quality
- Fallback to character-level tokenization if needed"

# Push to GitHub
echo "🌐 Pushing to GitHub..."
git push origin main

echo "✅ All changes committed and pushed successfully!"
echo ""
echo "📋 Next steps on remote machine:"
echo "   1. git pull origin main"
echo "   2. python train_custom_tokenizer.py"
echo "   3. python prepare_dataset.py"
echo "   4. ./launch_2gpu.sh"
echo ""
echo "🎉 Ready for much better text generation!"
