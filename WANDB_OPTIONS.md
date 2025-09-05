# W&B (Weights & Biases) Logging Options

## Overview
W&B is an optional logging service that provides beautiful visualizations of your training progress. You can choose to use it or not.

## Options

### 1. Console Logging Only (Default - No Account Needed)
```bash
# Run without W&B
./launch_2gpu.sh

# Or explicitly disable
WANDB_LOG=false ./launch_2gpu.sh
```

### 2. W&B Logging (Requires Free Account)
```bash
# Enable W&B logging
WANDB_LOG=true ./launch_2gpu.sh

# Or use the interactive launcher
./launch_with_choice.sh
```

### 3. Interactive Choice
```bash
# Choose your preference interactively
./launch_with_choice.sh
```

## What You Get with Each Option

### Console Logging Only
- ✅ **No account required**
- ✅ **All metrics printed to terminal**
- ✅ **Model checkpoints saved locally**
- ✅ **Works immediately**

### W&B Logging
- ✅ **Beautiful web dashboard**
- ✅ **Real-time training graphs**
- ✅ **Model comparison tools**
- ✅ **Experiment tracking**
- ❌ **Requires free W&B account**

## Creating a W&B Account (Optional)

1. Go to https://wandb.ai
2. Click "Sign Up" (free)
3. Create your account
4. Get your API key from https://wandb.ai/settings
5. Run: `wandb login` and paste your API key

## Environment Variables

```bash
# Disable W&B (default)
export WANDB_LOG=false

# Enable W&B
export WANDB_LOG=true

# Run training
./launch_2gpu.sh
```

## Troubleshooting

### W&B Not Installed
```bash
pip install wandb
```

### W&B Login Issues
```bash
wandb login
# Follow the prompts to get your API key
```

### W&B Disabled
If W&B fails, the script automatically falls back to console logging.

## Recommendation

- **For learning/experimentation**: Use console logging (no account needed)
- **For serious projects**: Use W&B logging (free account, better visualization)
