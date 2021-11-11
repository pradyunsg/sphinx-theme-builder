"""Compilation entrypoint."""

from typing import List

import click

from ..nodejs import generate_assets
from ..project import Project


class CompileCommand:
    """Compile the current project's assets."""

    interface: List[click.Parameter] = [
        click.Option(
            ["--production"],
            is_flag=True,
            default=False,
            help="Runs the build with `NODE_ENV=production` (`development` by default).",
        ),
    ]

    def run(self, production: bool) -> int:
        """Make it happen."""
        project = Project.from_cwd()
        generate_assets(project, production=production)
        return 0
