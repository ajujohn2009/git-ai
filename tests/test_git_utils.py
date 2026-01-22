"""Tests for git_utils module."""

import pytest
from pathlib import Path
import git
from git_ai.git_utils import GitRepo, GitError


class TestGitRepo:
    """Test GitRepo class."""

    def test_init_valid_repo(self, tmp_path):
        """Test initialization with valid git repository."""
        # Create a git repo
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        git.Repo.init(repo_path)

        # Should initialize without error
        git_repo = GitRepo(repo_path)
        assert git_repo.repo is not None

    def test_init_invalid_repo(self, tmp_path):
        """Test initialization with invalid git repository."""
        # Non-git directory
        non_repo = tmp_path / "not_a_repo"
        non_repo.mkdir()

        # Should raise GitError
        with pytest.raises(GitError, match="Not a git repository"):
            GitRepo(non_repo)

    def test_has_staged_changes_empty(self, tmp_path):
        """Test has_staged_changes with no changes."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        repo = git.Repo.init(repo_path)

        # Create initial commit
        test_file = repo_path / "test.txt"
        test_file.write_text("initial content")
        repo.index.add(["test.txt"])
        repo.index.commit("Initial commit")

        git_repo = GitRepo(repo_path)
        assert not git_repo.has_staged_changes()

    def test_has_staged_changes_with_changes(self, tmp_path):
        """Test has_staged_changes with staged changes."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        repo = git.Repo.init(repo_path)

        # Create initial commit
        test_file = repo_path / "test.txt"
        test_file.write_text("initial content")
        repo.index.add(["test.txt"])
        repo.index.commit("Initial commit")

        # Make changes and stage
        test_file.write_text("modified content")
        repo.index.add(["test.txt"])

        git_repo = GitRepo(repo_path)
        assert git_repo.has_staged_changes()

    def test_get_staged_files(self, tmp_path):
        """Test getting list of staged files."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        repo = git.Repo.init(repo_path)

        # Create initial commit
        test_file = repo_path / "test.txt"
        test_file.write_text("initial content")
        repo.index.add(["test.txt"])
        repo.index.commit("Initial commit")

        # Add new file
        new_file = repo_path / "new.txt"
        new_file.write_text("new content")
        repo.index.add(["new.txt"])

        git_repo = GitRepo(repo_path)
        staged_files = git_repo.get_staged_files()
        assert "new.txt" in staged_files

    def test_get_staged_diff_no_changes(self, tmp_path):
        """Test get_staged_diff with no staged changes."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        repo = git.Repo.init(repo_path)

        # Create initial commit
        test_file = repo_path / "test.txt"
        test_file.write_text("initial content")
        repo.index.add(["test.txt"])
        repo.index.commit("Initial commit")

        git_repo = GitRepo(repo_path)
        
        with pytest.raises(GitError, match="No staged changes"):
            git_repo.get_staged_diff()

    def test_get_diff_summary(self, tmp_path):
        """Test getting structured diff summary."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        repo = git.Repo.init(repo_path)

        # Create initial commit
        test_file = repo_path / "test.txt"
        test_file.write_text("initial content")
        repo.index.add(["test.txt"])
        repo.index.commit("Initial commit")

        # Modify file
        test_file.write_text("modified content")
        repo.index.add(["test.txt"])

        git_repo = GitRepo(repo_path)
        summary = git_repo.get_diff_summary()

        assert summary["modifications"] == 1
        assert len(summary["files_changed"]) == 1
        assert summary["files_changed"][0]["type"] == "M"

    def test_commit(self, tmp_path):
        """Test creating a commit."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        repo = git.Repo.init(repo_path)

        # Create initial commit
        test_file = repo_path / "test.txt"
        test_file.write_text("initial content")
        repo.index.add(["test.txt"])
        repo.index.commit("Initial commit")

        # Stage changes
        test_file.write_text("modified content")
        repo.index.add(["test.txt"])

        git_repo = GitRepo(repo_path)
        commit_hash = git_repo.commit("Test commit message")

        assert commit_hash is not None
        assert len(commit_hash) == 40  # SHA-1 hash length

    def test_get_recent_commits(self, tmp_path):
        """Test getting recent commits."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        repo = git.Repo.init(repo_path)

        # Create multiple commits
        for i in range(3):
            test_file = repo_path / f"test{i}.txt"
            test_file.write_text(f"content {i}")
            repo.index.add([f"test{i}.txt"])
            repo.index.commit(f"Commit {i}")

        git_repo = GitRepo(repo_path)
        recent = git_repo.get_recent_commits(count=2)

        assert len(recent) == 2
        assert "message" in recent[0]
        assert "hash" in recent[0]
