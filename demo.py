#!/usr/bin/env python3
"""Demo script to showcase git-ai features."""

import sys
import tempfile
from pathlib import Path
import git

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from git_ai.git_utils import GitRepo
from git_ai.llm_client import LLMClient
from git_ai.config import config
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def create_demo_repo():
    """Create a temporary demo repository."""
    temp_dir = Path(tempfile.mkdtemp(prefix="git-ai-demo-"))
    console.print(f"[dim]Creating demo repo at: {temp_dir}[/dim]\n")

    # Initialize repo
    repo = git.Repo.init(temp_dir)

    # Initial commit
    readme = temp_dir / "README.md"
    readme.write_text("# Demo Project\n\nThis is a demo project.")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")

    return temp_dir, repo


def demo_feature_addition(repo_path, repo):
    """Demo: Adding a new feature."""
    console.print("[bold cyan]Scenario 1: Adding a New Feature[/bold cyan]\n")

    # Create new files
    api_file = repo_path / "api.py"
    api_file.write_text("""
def get_user(user_id: int):
    '''Fetch user by ID from database.'''
    return database.query(User).filter_by(id=user_id).first()

def create_user(username: str, email: str):
    '''Create a new user.'''
    user = User(username=username, email=email)
    database.add(user)
    database.commit()
    return user
""")

    test_file = repo_path / "test_api.py"
    test_file.write_text("""
import pytest
from api import get_user, create_user

def test_create_user():
    user = create_user("testuser", "test@example.com")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
""")

    # Stage changes
    repo.index.add(["api.py", "test_api.py"])

    # Show what we're committing
    git_repo = GitRepo(repo_path)
    show_staged_changes(git_repo)

    # Generate commit message
    console.print("\n[bold green]Generated Commit Message:[/bold green]")
    diff = git_repo.get_staged_diff()
    diff_summary = git_repo.get_diff_summary()
    recent_commits = git_repo.get_recent_commits()

    # Simulate LLM generation (without actual API call)
    simulated_message = """feat(api): add user management endpoints

Implement user CRUD operations with database integration.
Includes get_user and create_user functions with proper
error handling and validation.

Add comprehensive unit tests for user operations."""

    console.print(Panel(simulated_message, border_style="green"))

    # Commit
    repo.index.commit(simulated_message)
    console.print("\n[green]✓ Commit created[/green]\n")


def demo_bug_fix(repo_path, repo):
    """Demo: Fixing a bug."""
    console.print("[bold cyan]Scenario 2: Bug Fix[/bold cyan]\n")

    # Modify existing file
    api_file = repo_path / "api.py"
    content = api_file.read_text()
    content = content.replace(
        "database.commit()",
        "database.commit()\n    return user"
    )
    api_file.write_text(content)

    # Stage changes
    repo.index.add(["api.py"])

    # Show what we're committing
    git_repo = GitRepo(repo_path)
    show_staged_changes(git_repo)

    # Simulated message
    simulated_message = """fix(api): return user object from create_user

Fix missing return statement in create_user function.
Previously returned None instead of created user object."""

    console.print("\n[bold green]Generated Commit Message:[/bold green]")
    console.print(Panel(simulated_message, border_style="green"))

    repo.index.commit(simulated_message)
    console.print("\n[green]✓ Commit created[/green]\n")


def demo_refactoring(repo_path, repo):
    """Demo: Refactoring code."""
    console.print("[bold cyan]Scenario 3: Code Refactoring[/bold cyan]\n")

    # Create utilities file
    utils_file = repo_path / "utils.py"
    utils_file.write_text("""
from typing import Optional

class DatabaseConnection:
    '''Database connection manager.'''
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        
    def query(self, model):
        '''Execute query for given model.'''
        pass
        
    def add(self, obj):
        '''Add object to database.'''
        pass
        
    def commit(self):
        '''Commit transaction.'''
        pass
""")

    # Update api.py to use new structure
    api_file = repo_path / "api.py"
    api_file.write_text("""
from utils import DatabaseConnection

db = DatabaseConnection("postgresql://localhost/demo")

def get_user(user_id: int):
    '''Fetch user by ID from database.'''
    return db.query(User).filter_by(id=user_id).first()

def create_user(username: str, email: str):
    '''Create a new user.'''
    user = User(username=username, email=email)
    db.add(user)
    db.commit()
    return user
""")

    # Stage changes
    repo.index.add(["api.py", "utils.py"])

    # Show what we're committing
    git_repo = GitRepo(repo_path)
    show_staged_changes(git_repo)

    # Simulated message
    simulated_message = """refactor(db): extract database connection to utils

Extract DatabaseConnection class to separate utils module
for better code organization and reusability. Update api.py
to use new database connection manager."""

    console.print("\n[bold green]Generated Commit Message:[/bold green]")
    console.print(Panel(simulated_message, border_style="green"))

    repo.index.commit(simulated_message)
    console.print("\n[green]✓ Commit created[/green]\n")


def show_staged_changes(git_repo):
    """Display staged changes."""
    summary = git_repo.get_diff_summary()

    table = Table(title="Staged Changes", show_header=True, header_style="bold cyan")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")

    status_map = {"A": "Added", "M": "Modified", "D": "Deleted"}
    for file_info in summary["files_changed"]:
        status = status_map.get(file_info["type"], file_info["type"])
        table.add_row(file_info["path"], status)

    console.print(table)


def show_commit_history(repo):
    """Show final commit history."""
    console.print("\n[bold cyan]Final Commit History:[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Hash", style="yellow")
    table.add_column("Message", style="white")

    for commit in repo.iter_commits(max_count=10):
        table.add_row(
            commit.hexsha[:7],
            commit.message.split("\n")[0]  # First line only
        )

    console.print(table)


def main():
    """Run the demo."""
    console.print(Panel.fit(
        "[bold cyan]git-ai Demo[/bold cyan]\n"
        "Watch how AI generates meaningful commit messages!",
        border_style="cyan"
    ))
    console.print()

    # Create demo repo
    repo_path, repo = create_demo_repo()

    try:
        # Run scenarios
        demo_feature_addition(repo_path, repo)
        input("Press Enter to continue...")
        console.print()

        demo_bug_fix(repo_path, repo)
        input("Press Enter to continue...")
        console.print()

        demo_refactoring(repo_path, repo)
        input("Press Enter to continue...")

        # Show final history
        show_commit_history(repo)

        console.print("\n[bold green]Demo Complete![/bold green]")
        console.print(f"[dim]Demo repo location: {repo_path}[/dim]")
        console.print("\n[bold]Try it yourself:[/bold]")
        console.print("  1. cd to any git repository")
        console.print("  2. Make changes and stage them: [cyan]git add .[/cyan]")
        console.print("  3. Run: [cyan]git-ai commit[/cyan]")

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")

    console.print()


if __name__ == "__main__":
    main()
