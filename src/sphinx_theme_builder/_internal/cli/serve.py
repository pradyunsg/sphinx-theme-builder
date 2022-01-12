import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import click

from ..errors import DiagnosticError
from ..project import Project
from ..ui import log


class ServeCommand:
    """Serve the provided documentation, with livereload on changes."""

    interface = [
        click.Option(
            ["--builder"],
            type=click.Choice(["html", "dirhtml"]),
            default="html",
            show_default=True,
            show_choices=True,
            help="The Sphinx builder to build the documentation with",
        ),
        click.Option(
            ["--port"],
            type=click.INT,
            default=0,
            show_default=True,
            show_choices=True,
            help="The port to start the server on. Uses a random free port by default.",
        ),
        click.Option(
            ["--open-browser / --no-open-browser"],
            is_flag=True,
            default=True,
            show_default=True,
            help="Open the browser after starting live-reload server.",
        ),
        click.Option(
            ["--override-theme / --no-override-theme"],
            is_flag=True,
            default=False,
            help="Override the `html_theme` value set in `conf.py`.",
        ),
        click.Argument(
            ["source_directory"],
            required=True,
            type=click.Path(
                exists=True,
                file_okay=False,
                dir_okay=True,
                allow_dash=True,
                resolve_path=True,
                path_type=Path,
            ),
        ),
    ]

    def run(
        self,
        *,
        port: int,
        source_directory: Path,
        builder: str,
        open_browser: bool,
        override_theme: bool,
    ) -> int:
        project = Project.from_cwd()

        with tempfile.TemporaryDirectory() as build_directory:
            command = [
                sys.executable,
                "-m",
                "sphinx_autobuild",
                # sphinx-autobuild flags
                f"--watch={os.fsdecode(project.source_path)}",
                f"--re-ignore=({'|'.join(map(re.escape, project.compiled_assets))})",
                f"--port={port}",  # use a random free port
                f"--pre-build='{sys.executable}' -m sphinx_theme_builder compile",
                # Sphinx flags
                "-T",
                "-a",  # full rebuild to ensure static assets are copied on each change
                f"-b={builder}",
                os.fsdecode(source_directory),
                os.fsdecode(build_directory),
            ]
            if open_browser:
                # open the browser for the user
                command.append("--open-browser")
            if override_theme:
                # override the theme, set in conf.py
                command.extend(["-D", f"html_theme={project.kebab_name}"])

            log("Invoking [bold]sphinx-autobuild[/] to run.")
            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as error:
                raise DiagnosticError(
                    reference="autobuild-failed",
                    message=f"[b]sphinx-autobuild[/] exited with a non-zero exit code {error.returncode}.",
                    context="See above for failure output from the underlying tooling.",
                    hint_stmt=None,
                ) from error
        return 0
