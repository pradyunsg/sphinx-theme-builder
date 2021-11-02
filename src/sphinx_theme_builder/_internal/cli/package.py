"""Compilation entrypoint."""

import subprocess
import sys
from typing import List

import click

from ..ui import log


class PackageCommand:
    """Generate Python distribution files. (sdist and wheel)"""

    interface: List[click.Parameter] = []

    def run(self) -> int:
        """Make it happen."""
        log("[magenta]$[/] [blue]python -m build[/]")
        subprocess.run([sys.executable, "-m", "build"], check=True)
        log("[green]Done![/]")
        return 0
