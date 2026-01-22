"""git-ai: AI-powered git commit message generator."""

__version__ = "0.1.0"
__author__ = "Aju John"
__email__ = "aju@ajujohn.me"

from .cli import main
from .git_utils import GitRepo
from .llm_client import LLMClient
from .config import config

__all__ = ["main", "GitRepo", "LLMClient", "config"]
