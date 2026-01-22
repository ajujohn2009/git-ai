# Quick Start Guide

Get started with git-ai in 3 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/ajujohn/git-ai.git
cd git-ai

# Install in development mode
pip install -e .
```

## Setup Your API Key

Choose one:

### Option 1: Anthropic (Recommended)

```bash
export ANTHROPIC_API_KEY=your-key-here
```

Get your key from: https://console.anthropic.com

### Option 2: OpenAI

```bash
export OPENAI_API_KEY=your-key-here
```

Get your key from: https://platform.openai.com

### Option 3: Local (Ollama)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Configure git-ai
git-ai config-set provider ollama
```

## First Commit

```bash
# Navigate to any git repository
cd your-project

# Make some changes
echo "console.log('hello');" > test.js

# Stage changes
git add test.js

# Generate and commit!
git-ai commit
```

That's it! 🎉

## Example Output

```
Staged Changes:
┏━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ File        ┃ Status   ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ test.js     │ Added    │
└─────────────┴──────────┘

1 file(s), 1 change(s)

✓ Analyzing changes...
✓ Generating commit message...

Generated commit message:
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ feat: add hello world example   ┃
┃                                 ┃
┃ Add simple JavaScript console   ┃
┃ log example for testing         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Options:
  a - Accept and commit
  r - Regenerate
  e - Edit manually
  f - Provide feedback for refinement
  c - Cancel

Choose [a/r/e/f/c] (a): a

✓ Commit created: a1b2c3d
```

## Pro Tips

### 1. Different Styles

```bash
# Conventional (default)
git-ai commit --style conventional

# With emojis
git-ai commit --style semantic

# Simple
git-ai commit --style simple
```

### 2. Quick Commit (No Editing)

```bash
git-ai commit --no-edit
```

### 3. Preview Only

```bash
git-ai commit --dry-run
```

### 4. Check Before Committing

```bash
git-ai status
```

## Troubleshooting

### "Not a git repository"

```bash
git init
```

### "No staged changes"

```bash
git add .
```

### API Key Not Working

```bash
# Check if set
echo $ANTHROPIC_API_KEY

# Set in .bashrc or .zshrc for persistence
echo 'export ANTHROPIC_API_KEY=your-key' >> ~/.bashrc
source ~/.bashrc
```

## Next Steps

- Run `git-ai --help` to see all commands
- Run `git-ai setup` for interactive configuration
- Check `README.md` for advanced features

---

**Need help?** Open an issue: https://github.com/ajujohn/git-ai/issues
