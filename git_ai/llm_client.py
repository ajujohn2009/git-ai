"""LLM client for generating commit messages."""

from typing import Optional
import anthropic
import openai
from .config import config


class LLMClient:
    """LLM client with multi-provider support."""

    def __init__(self, provider: Optional[str] = None):
        """Initialize LLM client.
        
        Args:
            provider: LLM provider (anthropic, openai, ollama). Defaults to config.
        """
        self.provider = provider or config.provider
        self.model = config.model

        if self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=config.api_key)
        elif self.provider == "openai":
            self.client = openai.OpenAI(api_key=config.api_key)
        elif self.provider == "ollama":
            # Ollama runs locally, no API key needed
            self.client = openai.OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"  # Dummy key for Ollama
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def generate_commit_message(
        self,
        diff: str,
        diff_summary: dict,
        recent_commits: list[dict],
        style: str = "conventional",
    ) -> str:
        """Generate commit message from git diff.
        
        Args:
            diff: Git diff text.
            diff_summary: Structured summary of changes.
            recent_commits: Recent commit messages for context.
            style: Commit message style (conventional, semantic, simple).
            
        Returns:
            Generated commit message.
        """
        # Truncate diff if too long
        max_length = config.get("max_diff_length", 4000)
        if len(diff) > max_length:
            diff = diff[:max_length] + "\n... (diff truncated)"

        prompt = self._build_prompt(diff, diff_summary, recent_commits, style)

        if self.provider == "anthropic":
            return self._generate_anthropic(prompt)
        else:  # openai or ollama
            return self._generate_openai(prompt)

    def _build_prompt(
        self,
        diff: str,
        diff_summary: dict,
        recent_commits: list[dict],
        style: str,
    ) -> str:
        """Build prompt for LLM.
        
        Args:
            diff: Git diff text.
            diff_summary: Structured summary of changes.
            recent_commits: Recent commit messages for context.
            style: Commit message style.
            
        Returns:
            Formatted prompt.
        """
        commit_types = ", ".join(config.commit_types)
        
        files_changed = "\n".join([
            f"- {f['path']} ({f['type']})"
            for f in diff_summary["files_changed"]
        ])

        recent_context = ""
        if recent_commits:
            recent_context = "\n\nRecent commits for context:\n" + "\n".join([
                f"- {c['hash']}: {c['message']}"
                for c in recent_commits[:3]
            ])

        if style == "conventional":
            format_guide = f"""
Format: <type>(<scope>): <subject>

<body>

Types: {commit_types}
- Use feat: for new features
- Use fix: for bug fixes
- Use docs: for documentation
- Use refactor: for code refactoring
- Use test: for test changes
- Use chore: for maintenance tasks

Rules:
1. Subject line max 50 chars, lowercase, no period
2. Body wraps at 72 chars
3. Explain WHAT and WHY, not HOW
4. Use imperative mood ("add" not "added")
"""
        elif style == "semantic":
            format_guide = """
Format: <emoji> <type>: <subject>

Examples:
✨ feat: add user authentication
🐛 fix: resolve memory leak in worker
📝 docs: update API documentation
♻️ refactor: simplify database queries
"""
        else:  # simple
            format_guide = """
Format: <subject>

<body>

Keep it simple and clear. Focus on what changed and why.
"""

        prompt = f"""Generate a git commit message for the following changes.

Files changed:
{files_changed}

Summary:
- {diff_summary['additions']} file(s) added
- {diff_summary['modifications']} file(s) modified
- {diff_summary['deletions']} file(s) deleted

{format_guide}

Git diff:
```
{diff}
```
{recent_context}

Generate a clear, concise commit message. Return ONLY the commit message, no explanations."""

        return prompt

    def _generate_anthropic(self, prompt: str) -> str:
        """Generate using Anthropic API."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=config.get("temperature", 0.3),
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def _generate_openai(self, prompt: str) -> str:
        """Generate using OpenAI API or Ollama."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=config.get("temperature", 0.3),
        )
        return response.choices[0].message.content.strip()

    def refine_message(self, original: str, feedback: str) -> str:
        """Refine commit message based on user feedback.
        
        Args:
            original: Original commit message.
            feedback: User feedback for refinement.
            
        Returns:
            Refined commit message.
        """
        prompt = f"""Refine this commit message based on the feedback.

Original message:
{original}

Feedback:
{feedback}

Generate the refined commit message. Return ONLY the commit message, no explanations."""

        if self.provider == "anthropic":
            return self._generate_anthropic(prompt)
        else:
            return self._generate_openai(prompt)
