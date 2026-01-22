"""Command-line interface for git-ai."""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich import print as rprint

from .git_utils import GitRepo, GitError
from .llm_client import LLMClient
from .config import config

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AI-powered git commit message generator."""
    pass


@cli.command()
@click.option("--style", type=click.Choice(["conventional", "semantic", "simple"]), 
              default="conventional", help="Commit message style")
@click.option("--dry-run", is_flag=True, help="Generate message without committing")
@click.option("--no-edit", is_flag=True, help="Skip interactive editing")
@click.option("--provider", type=click.Choice(["anthropic", "openai", "ollama"]), 
              help="LLM provider to use")
def commit(style: str, dry_run: bool, no_edit: bool, provider: str):
    """Generate and create a commit with AI-generated message."""
    try:
        # Initialize
        repo = GitRepo()
        
        if provider:
            config.set("provider", provider)
        
        llm = LLMClient()

        # Check for staged changes
        if not repo.has_staged_changes():
            console.print("[red]No staged changes found.[/red]")
            console.print("Use [cyan]git add[/cyan] to stage your changes first.")
            sys.exit(1)

        # Show what's being committed
        _show_staged_changes(repo)

        # Get diff and generate message
        with console.status("[bold green]Analyzing changes..."):
            diff = repo.get_staged_diff()
            diff_summary = repo.get_diff_summary()
            recent_commits = repo.get_recent_commits()

        with console.status("[bold green]Generating commit message..."):
            message = llm.generate_commit_message(
                diff, diff_summary, recent_commits, style
            )

        # Display generated message
        console.print("\n[bold green]Generated commit message:[/bold green]")
        console.print(Panel(message, border_style="green"))

        # Interactive editing unless --no-edit
        if not no_edit:
            message = _interactive_edit(message, llm, dry_run)

        # Commit or dry-run
        if dry_run:
            console.print("\n[yellow]Dry run - no commit created.[/yellow]")
            console.print("Message copied to clipboard (if available)")
        else:
            if Confirm.ask("\n[bold]Create commit with this message?[/bold]", default=True):
                commit_hash = repo.commit(message)
                console.print(f"\n[green]✓ Commit created:[/green] {commit_hash[:7]}")
            else:
                console.print("[yellow]Commit cancelled.[/yellow]")

    except GitError as e:
        console.print(f"[red]Git Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
def status():
    """Show git status and staged changes."""
    try:
        repo = GitRepo()
        _show_staged_changes(repo)
    except GitError as e:
        console.print(f"[red]Git Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set configuration value."""
    try:
        # Handle nested keys like model.anthropic
        if "." in key:
            parts = key.split(".")
            current = config.config
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            config.set(key, value)
        
        config.save_config()
        console.print(f"[green]✓ Configuration updated:[/green] {key} = {value}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("key", required=False)
def config_get(key: str):
    """Get configuration value(s)."""
    if key:
        value = config.get(key)
        console.print(f"{key}: {value}")
    else:
        # Show all config
        table = Table(title="git-ai Configuration")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")

        for k, v in config.config.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    table.add_row(f"{k}.{sub_k}", str(sub_v))
            else:
                table.add_row(k, str(v))

        console.print(table)


@cli.command()
def setup():
    """Interactive setup wizard."""
    console.print(Panel.fit(
        "[bold cyan]git-ai Setup Wizard[/bold cyan]\n"
        "Let's configure your AI commit message generator!",
        border_style="cyan"
    ))

    # Choose provider
    console.print("\n[bold]1. Choose LLM Provider:[/bold]")
    console.print("  [cyan]anthropic[/cyan] - Claude (recommended)")
    console.print("  [cyan]openai[/cyan] - GPT models")
    console.print("  [cyan]ollama[/cyan] - Local models")
    
    provider = Prompt.ask(
        "Provider",
        choices=["anthropic", "openai", "ollama"],
        default=config.provider
    )
    config.set("provider", provider)

    # API Key
    if provider != "ollama":
        console.print(f"\n[bold]2. {provider.title()} API Key:[/bold]")
        console.print(f"Get your key from: {'https://console.anthropic.com' if provider == 'anthropic' else 'https://platform.openai.com'}")
        console.print("Set it in your environment:")
        env_var = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
        console.print(f"  [cyan]export {env_var}=your-key-here[/cyan]")

    # Commit style
    console.print("\n[bold]3. Default Commit Style:[/bold]")
    style = Prompt.ask(
        "Style",
        choices=["conventional", "semantic", "simple"],
        default="conventional"
    )
    config.set("default_style", style)

    # Save
    config.save_config()
    console.print("\n[green]✓ Setup complete![/green]")
    console.print(f"Config saved to: {config.config_path}")


def _show_staged_changes(repo: GitRepo):
    """Display staged changes in a nice format."""
    summary = repo.get_diff_summary()
    files_changed, total_changes = repo.get_commit_stats()

    console.print("\n[bold]Staged Changes:[/bold]")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")

    for file_info in summary["files_changed"]:
        status_map = {"A": "Added", "M": "Modified", "D": "Deleted", "R": "Renamed"}
        status = status_map.get(file_info["type"], file_info["type"])
        table.add_row(file_info["path"], status)

    console.print(table)
    console.print(f"\n[dim]{files_changed} file(s), {total_changes} change(s)[/dim]")


def _interactive_edit(message: str, llm: LLMClient, dry_run: bool) -> str:
    """Interactive message editing loop."""
    current_message = message

    while True:
        console.print("\n[bold]Options:[/bold]")
        console.print("  [cyan]a[/cyan] - Accept and commit")
        console.print("  [cyan]r[/cyan] - Regenerate")
        console.print("  [cyan]e[/cyan] - Edit manually")
        console.print("  [cyan]f[/cyan] - Provide feedback for refinement")
        console.print("  [cyan]c[/cyan] - Cancel")

        choice = Prompt.ask("Choose", choices=["a", "r", "e", "f", "c"], default="a")

        if choice == "a":
            return current_message
        elif choice == "r":
            with console.status("[bold green]Regenerating..."):
                # Re-generate with slightly different temperature
                original_temp = config.get("temperature", 0.3)
                config.set("temperature", min(original_temp + 0.2, 1.0))
                
                # This would need the original parameters - simplified here
                console.print("[yellow]Feature coming soon: regeneration with variation[/yellow]")
                
                config.set("temperature", original_temp)
        elif choice == "e":
            console.print("\n[dim]Enter your commit message (Ctrl+D or Ctrl+Z when done):[/dim]")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                current_message = "\n".join(lines)
                console.print("\n[bold green]Updated message:[/bold green]")
                console.print(Panel(current_message, border_style="green"))
        elif choice == "f":
            feedback = Prompt.ask("\n[bold]What would you like to change?[/bold]")
            with console.status("[bold green]Refining message..."):
                current_message = llm.refine_message(current_message, feedback)
                console.print("\n[bold green]Refined message:[/bold green]")
                console.print(Panel(current_message, border_style="green"))
        elif choice == "c":
            sys.exit(0)

    return current_message


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
