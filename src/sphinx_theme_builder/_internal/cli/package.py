"""Compilation entrypoint."""

import subprocess
import sys

import click

from ..ui import log


class PackageCommand:
    """Generate Python distribution files. (sdist and wheel)"""

    interface: list[click.Parameter] = []

    def run(self) -> int:
        """Make it happen."""
        log("[magenta]$[/] [blue]python -m build[/]")
        try:
            subprocess.run([sys.executable, "-m", "build"], check=True)
        except subprocess.CalledProcessError as error:
            return error.returncode
        log("[green]Done![/]")
        return 0
