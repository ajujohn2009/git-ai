# git-ai 🤖

AI-powered git commit message generator that analyzes your changes and creates meaningful, conventional commit messages.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

✨ **Multi-Provider Support**: Use Claude (Anthropic), GPT (OpenAI), or local models (Ollama)  
📝 **Multiple Styles**: Conventional commits, semantic commits, or simple messages  
🎨 **Interactive Mode**: Edit, refine, or regenerate messages before committing  
⚡ **Smart Analysis**: Considers file changes, diff content, and recent commit history  
🔧 **Configurable**: Customize commit types, formats, and preferences  
💰 **Cost Optimized**: Optional TOON format integration for reduced API costs

## Installation

### From PyPI (when published)

```bash
pip install git-ai
```

### From Source

```bash
git clone https://github.com/ajujohn/git-ai.git
cd git-ai
pip install -e .
```

## Quick Start

### 1. Setup

Run the interactive setup wizard:

```bash
git-ai setup
```

Or manually set your API key:

```bash
# For Anthropic (recommended)
export ANTHROPIC_API_KEY=your-key-here

# For OpenAI
export OPENAI_API_KEY=your-key-here
```

### 2. Generate a Commit

Stage your changes and run:

```bash
git add .
git-ai commit
```

That's it! git-ai will:
- Analyze your staged changes
- Generate a meaningful commit message
- Let you review and edit if needed
- Create the commit

## Usage Examples

### Basic Usage

```bash
# Stage changes and commit
git add .
git-ai commit
```

### Different Styles

```bash
# Conventional commits (default)
git-ai commit --style conventional

# Semantic commits with emojis
git-ai commit --style semantic

# Simple, straightforward messages
git-ai commit --style simple
```

### Advanced Options

```bash
# Generate without committing
git-ai commit --dry-run

# Skip interactive editing
git-ai commit --no-edit

# Use specific provider
git-ai commit --provider openai
```

### Configuration

```bash
# View all config
git-ai config-get

# Set default provider
git-ai config-set provider anthropic

# Set default style
git-ai config-set default_style conventional

# Change model
git-ai config-set model.anthropic claude-sonnet-4-20250514
```

### Check Status

```bash
# View staged changes
git-ai status
```

## Commit Message Styles

### Conventional Commits

```
feat(auth): add JWT authentication

Implement JWT-based authentication system with refresh tokens.
Includes middleware for protecting routes and token validation.
```

### Semantic Commits

```
✨ feat: add JWT authentication

Implement JWT-based authentication with refresh token support
```

### Simple

```
Add JWT authentication

Implement authentication system with JWT tokens and refresh mechanism
```

## Configuration

Configuration is stored in `~/.git-ai/config.yaml`.

### Default Configuration

```yaml
provider: anthropic
model:
  anthropic: claude-sonnet-4-20250514
  openai: gpt-4-turbo-preview
  ollama: llama2
commit_types:
  - feat
  - fix
  - docs
  - style
  - refactor
  - perf
  - test
  - chore
  - ci
  - build
max_diff_length: 4000
temperature: 0.3
use_toon: false
```

### Customization

```bash
# Add custom commit types
git-ai config-set commit_types "feat,fix,docs,custom"

# Adjust creativity (0.0 - 1.0)
git-ai config-set temperature 0.5

# Enable TOON format for cost optimization
git-ai config-set use_toon true
```

## Interactive Mode

When you run `git-ai commit`, you'll see:

```
Generated commit message:
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ feat(api): add user endpoints    ┃
┃                                  ┃
┃ Add CRUD endpoints for user      ┃
┃ management with authentication   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Options:
  a - Accept and commit
  r - Regenerate
  e - Edit manually
  f - Provide feedback for refinement
  c - Cancel
```

## Using Local Models (Ollama)

Install [Ollama](https://ollama.ai) and pull a model:

```bash
ollama pull llama2
```

Configure git-ai:

```bash
git-ai config-set provider ollama
git-ai config-set model.ollama llama2
```

## API Cost Optimization

git-ai uses smart strategies to minimize API costs:

- **Diff Truncation**: Limits diff size to essential content
- **Context Pruning**: Only includes relevant recent commits
- **Temperature Control**: Lower temperature for more focused output
- **TOON Format** (optional): Uses token-optimized format for additional savings

Enable TOON:

```bash
git-ai config-set use_toon true
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/ajujohn/git-ai.git
cd git-ai
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
pytest --cov=git_ai
```

### Code Quality

```bash
# Format code
black git_ai tests

# Lint
ruff check git_ai tests
```

## How It Works

1. **Analyzes Changes**: Reads git diff and file changes
2. **Gathers Context**: Checks recent commits and repository state
3. **Generates Message**: Uses LLM to create appropriate commit message
4. **Interactive Review**: Lets you refine before committing
5. **Creates Commit**: Applies the message and commits

## Supported Providers

| Provider | Models | Setup |
|----------|--------|-------|
| Anthropic | Claude 4.5 (Opus, Sonnet, Haiku) | `ANTHROPIC_API_KEY` |
| OpenAI | GPT-4, GPT-3.5 | `OPENAI_API_KEY` |
| Ollama | Llama2, Mistral, etc. | Local installation |

## Requirements

- Python 3.9+
- Git repository
- API key (Anthropic or OpenAI) or Ollama installation

## Troubleshooting

### "Not a git repository"

Make sure you're in a git repository:

```bash
git init  # Initialize if needed
```

### "No staged changes found"

Stage your changes first:

```bash
git add .
# or
git add specific-file.py
```

### API Key Issues

Verify your API key is set:

```bash
echo $ANTHROPIC_API_KEY
# or
echo $OPENAI_API_KEY
```

### Rate Limiting

If you hit rate limits, try:
- Using a local model with Ollama
- Reducing diff size with selective staging
- Adding delays between commits

## Roadmap

- [ ] GitHub Actions integration
- [ ] Pre-commit hook support
- [ ] VS Code extension
- [ ] Commit message templates
- [ ] Multi-language support
- [ ] Batch processing for multiple commits
- [ ] Git hook installer

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Aju John**
- Website: [ajujohn.me](https://ajujohn.me)
- GitHub: [@ajujohn](https://github.com/ajujohn)

## Acknowledgments

- Inspired by conventional commits specification
- Built with Claude 4.5 for AI generation
- Uses GitPython for git operations

---

⭐ If you find this useful, please star the repository!

💡 Have suggestions? Open an issue or PR!
