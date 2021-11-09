"""Used to initialise the project, with the correct scaffolding."""

import subprocess
from pathlib import Path
from typing import List, Tuple

import click

from ..errors import DiagnosticError
from ..nodejs import _NODEENV_DIR as NODEENV_DIRNAME
from ..nodejs import run_in


class NpmCommand:
    """Interact with the npm, available in the environment.

    If you want to run `npm --help`, use `--` to separate the options for npm:

        stb npm -- --help
    """

    context_settings = dict(
        ignore_unknown_options=True,
    )
    interface: List[click.Parameter] = [
        click.Argument(["arguments"], nargs=-1, type=click.UNPROCESSED),
    ]

    def run(self, arguments: Tuple[str]) -> int:
        nodeenv = Path.cwd() / NODEENV_DIRNAME
        if not nodeenv.exists():
            raise DiagnosticError(
                message="Could not find the `.nodeenv` directory to use.",
                context=str(nodeenv),
                hint_stmt="Did you run `stb compile` yet?",
                reference="no-nodeenv",
            )

        try:
            run_in(nodeenv, ["npm"] + list(arguments))
        except subprocess.CalledProcessError as error:
            return error.returncode
        else:
            return 0
