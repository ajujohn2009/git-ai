"""Configuration management for git-ai."""

import os
from pathlib import Path
from typing import Optional
import yaml
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration manager for git-ai."""

    DEFAULT_CONFIG = {
        "provider": "anthropic",  # anthropic, openai, ollama
        "model": {
            "anthropic": "claude-sonnet-4-20250514",
            "openai": "gpt-4-turbo-preview",
            "ollama": "llama2",
        },
        "commit_types": [
            "feat",
            "fix",
            "docs",
            "style",
            "refactor",
            "perf",
            "test",
            "chore",
            "ci",
            "build",
        ],
        "max_diff_length": 4000,  # characters
        "temperature": 0.3,
        "use_toon": False,  # Enable TOON format for cost optimization
    }

    def __init__(self):
        self.config_path = Path.home() / ".git-ai" / "config.yaml"
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file or use defaults."""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                user_config = yaml.safe_load(f)
                return {**self.DEFAULT_CONFIG, **user_config}
        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        """Save current configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """Set configuration value."""
        self.config[key] = value

    @property
    def provider(self) -> str:
        """Get current LLM provider."""
        return self.config["provider"]

    @property
    def model(self) -> str:
        """Get model for current provider."""
        return self.config["model"][self.provider]

    @property
    def api_key(self) -> Optional[str]:
        """Get API key for current provider."""
        if self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        elif self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        return None

    @property
    def commit_types(self) -> list:
        """Get allowed commit types."""
        return self.config["commit_types"]


# Global config instance
config = Config()
