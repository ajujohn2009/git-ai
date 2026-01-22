"""Git operations and diff analysis."""

from typing import Optional, Tuple
import git
from pathlib import Path


class GitError(Exception):
    """Custom exception for git-related errors."""
    pass


class GitRepo:
    """Git repository operations."""

    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize GitRepo.
        
        Args:
            repo_path: Path to git repository. Defaults to current directory.
        """
        try:
            self.repo = git.Repo(repo_path or Path.cwd(), search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            raise GitError("Not a git repository")

    def get_staged_diff(self) -> str:
        """Get diff of staged changes.
        
        Returns:
            Diff string of staged changes.
            
        Raises:
            GitError: If no changes are staged.
        """
        if not self.has_staged_changes():
            raise GitError("No staged changes found. Use 'git add' to stage changes.")

        # Get diff of staged changes
        diff = self.repo.git.diff("--cached", "--no-color")
        return diff

    def get_staged_files(self) -> list[str]:
        """Get list of staged files.
        
        Returns:
            List of staged file paths.
        """
        return [item.a_path for item in self.repo.index.diff("HEAD")]

    def has_staged_changes(self) -> bool:
        """Check if there are staged changes.
        
        Returns:
            True if there are staged changes, False otherwise.
        """
        return len(self.repo.index.diff("HEAD")) > 0

    def commit(self, message: str) -> str:
        """Create a commit with the given message.
        
        Args:
            message: Commit message.
            
        Returns:
            Commit hash.
        """
        commit = self.repo.index.commit(message)
        return commit.hexsha

    def get_commit_stats(self) -> Tuple[int, int]:
        """Get statistics about staged changes.
        
        Returns:
            Tuple of (files_changed, total_changes).
        """
        diff = self.repo.index.diff("HEAD")
        files_changed = len(diff)
        
        # Count insertions and deletions
        diff_text = self.repo.git.diff("--cached", "--shortstat")
        total_changes = 0
        
        if diff_text:
            # Parse shortstat output: "2 files changed, 10 insertions(+), 3 deletions(-)"
            parts = diff_text.split(",")
            for part in parts[1:]:  # Skip files changed part
                if "insertion" in part or "deletion" in part:
                    num = int(part.strip().split()[0])
                    total_changes += num
        
        return files_changed, total_changes

    def get_diff_summary(self) -> dict:
        """Get structured summary of staged changes.
        
        Returns:
            Dictionary with diff summary including files and change types.
        """
        diff = self.repo.index.diff("HEAD")
        
        summary = {
            "files_changed": [],
            "additions": 0,
            "deletions": 0,
            "modifications": 0,
        }

        for item in diff:
            change_type = item.change_type
            file_path = item.a_path or item.b_path

            summary["files_changed"].append({
                "path": file_path,
                "type": change_type,
            })

            if change_type == "A":
                summary["additions"] += 1
            elif change_type == "D":
                summary["deletions"] += 1
            elif change_type == "M":
                summary["modifications"] += 1

        return summary

    def get_recent_commits(self, count: int = 5) -> list[dict]:
        """Get recent commit messages for context.
        
        Args:
            count: Number of recent commits to retrieve.
            
        Returns:
            List of commit dictionaries with message and hash.
        """
        commits = []
        for commit in self.repo.iter_commits(max_count=count):
            commits.append({
                "hash": commit.hexsha[:7],
                "message": commit.message.strip(),
                "author": commit.author.name,
            })
        return commits
