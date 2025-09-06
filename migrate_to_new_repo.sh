#!/bin/bash
# Migration script for helloLondon repository

echo "🏛️ Migrating to helloLondon repository..."
echo "=========================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Please run this from the project root."
    exit 1
fi

# Check current status
echo "📊 Current git status:"
git status --short

# Ask for confirmation
read -p "Do you want to proceed with migration? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Migration cancelled."
    exit 1
fi

# Add and commit any uncommitted changes
echo "💾 Committing any uncommitted changes..."
git add .
git commit -m "Final cleanup before migration to helloLondon repo" || echo "No changes to commit"

# Add new remote
echo "🔗 Adding new remote repository..."
git remote add origin https://github.com/bahree/helloLondon.git || echo "Remote already exists"

# Create dev branch
echo "🌿 Creating dev branch..."
git checkout -b dev

# Push dev branch
echo "📤 Pushing dev branch..."
git push -u origin dev

# Switch back to main and push
echo "📤 Pushing main branch..."
git checkout main
git push -u origin main

# Verify setup
echo "✅ Verifying setup..."
git remote -v
git branch -a

echo "🎉 Migration complete!"
echo "Repository: https://github.com/bahree/helloLondon"
echo "Main branch: main"
echo "Dev branch: dev"
echo ""
echo "Next steps:"
echo "1. Go to GitHub and set up branch protection rules"
echo "2. Switch to dev branch: git checkout dev"
echo "3. Start development work"
