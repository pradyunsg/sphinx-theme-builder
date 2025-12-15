"""Used to initialise the project, with the correct scaffolding."""

import os
import subprocess
import sys
from pathlib import Path

import click

from ..errors import STBError
from ..ui import log

_TEMPLATE_URL = "https://github.com/pradyunsg/sphinx-theme-template/archive/refs/heads/sphinx-theme-template-stable.zip"


class NewCommand:
    """Create a new project."""

    interface: list[click.Parameter] = [
        click.Argument(
            ["source_directory"],
            required=True,
            type=click.Path(
                exists=False,
                file_okay=False,
                dir_okay=True,
                writable=True,
                path_type=Path,
            ),
        ),
    ]

    def run(self, source_directory: Path) -> int:
        log(f"[yellow]#[/] Looking at [magenta]{source_directory}[/]")

        pyproject_toml = source_directory / "pyproject.toml"
        setup_py = source_directory / "setup.py"
        if pyproject_toml.exists() or setup_py.exists():
            raise STBError(
                code="can-not-overwrite-existing-python-project",
                message="Refusing to generate a new project in provided directory.",
                causes=[
                    "This directory contains a Python project, which will not be "
                    "overwritten."
                ],
                hint_stmt=(
                    "This command should be used on empty/non-existing directories."
                ),
            )

        command = [
            sys.executable,
            "-m",
            "cookiecutter",
            "-o",
            os.fsdecode(source_directory),
            _TEMPLATE_URL,
        ]
        log(f"[magenta]$[/] python {' '.join(command[1:])}")
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as error:
            raise STBError(
                code="cookiecutter-failed",
                message="Cookiecutter failed to generate the project.",
                causes=[f"Exit code: {error.returncode}"],
                note_stmt="cookiecutter's failure output is available above.",
                hint_stmt=(
                    "[b]@pradyunsg[/] might still need to write/update the supporting "
                    "cookiecutter template. :sweat_smile:"
                ),
            ) from error

        return 0
