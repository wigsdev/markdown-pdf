"""Command-line interface for MDPDF."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from mdpdf import __version__
from mdpdf.config import AVAILABLE_THEMES, ConversionConfig
from mdpdf.converter import Converter
from mdpdf.exceptions import MdpdfError
from mdpdf.utils import find_markdown_files

app = typer.Typer(
    name="mdpdf",
    help="High-quality Markdown to PDF converter.",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()
error_console = Console(stderr=True)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"[bold blue]mdpdf[/bold blue] v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version", "-v", help="Show version.", callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """MDPDF - Convert Markdown to styled PDF documents."""


@app.command()
def convert(
    files: Annotated[
        list[Path],
        typer.Argument(help="Markdown file(s) to convert.", exists=True),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output directory."),
    ] = None,
    style: Annotated[
        str,
        typer.Option("--style", "-s", help="Theme name."),
    ] = "default",
    toc: Annotated[
        bool,
        typer.Option("--toc/--no-toc", help="Include table of contents."),
    ] = True,
    toc_level: Annotated[
        int,
        typer.Option("--toc-level", help="Max heading level for TOC (1-6).", min=1, max=6),
    ] = 3,
    config_file: Annotated[
        Optional[Path],
        typer.Option("--config", "-c", help="Path to config file."),
    ] = None,
    verbose: Annotated[
        bool, typer.Option("--verbose", help="Verbose output."),
    ] = False,
    quiet: Annotated[
        bool, typer.Option("--quiet", "-q", help="Suppress output."),
    ] = False,
) -> None:
    """Convert Markdown files to PDF."""
    try:
        config = ConversionConfig.load(config_file)
    except MdpdfError as e:
        error_console.print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(code=1) from e

    # Apply CLI overrides
    if output:
        config.output.directory = output
    config.style.theme = style
    config.style.toc = toc
    config.style.toc_level = toc_level
    config.verbose = verbose

    converter = Converter(config)
    success_count = 0
    error_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=quiet,
    ) as progress:
        task = progress.add_task("Converting...", total=len(files))

        for input_file in files:
            progress.update(task, description=f"Converting {input_file.name}...")
            try:
                result = converter.convert(input_file)
                success_count += 1
                if verbose and not quiet:
                    console.print(f"  [green]✓[/green] {input_file.name} → {result.output_path}")
            except MdpdfError as e:
                error_count += 1
                if not quiet:
                    error_console.print(f"  [red]✗[/red] {input_file.name}: {e}")
            progress.advance(task)

    if not quiet:
        if success_count > 0:
            console.print(f"\n[green]✓ Converted {success_count} file(s)[/green]")
        if error_count > 0:
            console.print(f"[red]✗ Failed {error_count} file(s)[/red]")

    if error_count > 0:
        raise typer.Exit(code=1)


@app.command("list-styles")
def list_styles() -> None:
    """Show available themes."""
    table = Table(title="Available Themes")
    table.add_column("Theme", style="cyan")
    table.add_column("Description")

    descriptions = {
        "default": "Clean, professional, light background",
        "monokai": "Dark theme with vibrant colors",
        "github": "GitHub-style dark code blocks",
        "solarized-dark": "Solarized color scheme (dark)",
        "solarized-light": "Solarized color scheme (light)",
    }

    for theme in AVAILABLE_THEMES:
        table.add_row(theme, descriptions.get(theme, ""))

    console.print(table)


@app.command()
def batch(
    directory: Annotated[
        Path,
        typer.Argument(help="Directory to search for Markdown files.", exists=True),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output directory."),
    ] = None,
    style: Annotated[
        str, typer.Option("--style", "-s", help="Theme name."),
    ] = "default",
    recursive: Annotated[
        bool, typer.Option("--recursive/--no-recursive", help="Search subdirs."),
    ] = True,
    quiet: Annotated[
        bool, typer.Option("--quiet", "-q", help="Suppress output."),
    ] = False,
) -> None:
    """Convert all Markdown files in a directory."""
    files = find_markdown_files(directory, recursive=recursive)

    if not files:
        if not quiet:
            console.print("[yellow]No Markdown files found.[/yellow]")
        raise typer.Exit()

    if not quiet:
        console.print(f"Found {len(files)} Markdown file(s)")

    config = ConversionConfig()
    if output:
        config.output.directory = output
    config.style.theme = style

    converter = Converter(config)
    results = converter.convert_batch(files, output_dir=output)

    successes = sum(1 for r in results if r.success)
    failures = sum(1 for r in results if not r.success)

    if not quiet:
        console.print(f"\n[green]✓ Converted: {successes}[/green]")
        if failures:
            console.print(f"[red]✗ Failed: {failures}[/red]")

    if failures:
        raise typer.Exit(code=1)


@app.command()
def init(
    path: Annotated[
        Path, typer.Argument(help="Directory for config file."),
    ] = Path("."),
) -> None:
    """Create a configuration file template."""
    config_path = path / ".mdpdf.yaml"

    if config_path.exists():
        overwrite = typer.confirm(f"Config exists at {config_path}. Overwrite?")
        if not overwrite:
            raise typer.Exit()

    config_content = """\
# MDPDF Configuration
# See: https://github.com/WIGUSA/markdown-pdf

output:
  # directory: ./pdfs
  create_if_missing: true
  overwrite: true

style:
  theme: default  # Options: default, monokai, github, solarized-dark, solarized-light
  toc: true
  toc_level: 3
  # custom_css: ./custom.css

# verbose: false
"""
    config_path.write_text(config_content, encoding="utf-8")
    console.print(f"[green]✓[/green] Created {config_path}")


@app.command()
def serve(
    port: Annotated[
        int, typer.Option("--port", "-p", help="Server port."),
    ] = 8000,
    host: Annotated[
        str, typer.Option("--host", help="Server host."),
    ] = "127.0.0.1",
) -> None:
    """Start the web interface server."""
    try:
        import uvicorn
    except ImportError:
        error_console.print(
            "[red]Web dependencies not installed.[/red]\n"
            "Install with: pip install mdpdf[web]"
        )
        raise typer.Exit(code=1)

    console.print(f"Starting server at http://{host}:{port}")
    uvicorn.run("web.backend.main:app", host=host, port=port, reload=False)
