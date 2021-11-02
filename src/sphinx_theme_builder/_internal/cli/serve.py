import os
import subprocess
import sys
import tempfile
from pathlib import Path

import click

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
        source_directory: Path,
        builder: str,
        open_browser: bool,
        override_theme: bool,
    ) -> int:
        project = Project.from_cwd()
        log("Invoking [bold]sphinx-autobuild[/] to run.")

        # Hard-coded for now, will be determined automatically later.
        with tempfile.TemporaryDirectory() as build_directory:
            command = [
                sys.executable,
                "-m",
                "sphinx_autobuild",
                "--watch",
                os.fsdecode(project.theme_path),
                f"--ignore={project.output_script_path}",
                f"--ignore={project.output_stylesheet_path}",
                f"--ignore={project.output_extension_stylesheet_path}",
                "-a",  # rebuild all pages on change, to ensure theme changes are reflected.
                f"-b={builder}",
                "--pre-build",
                f"{sys.executable} -m sphinx_theme_builder compile",
                os.fsdecode(source_directory),
                os.fsdecode(build_directory),
            ]
            if open_browser:
                # open the browser for the user
                command.append("--open-browser")
            if override_theme:
                # override the theme, set in conf.py
                command.extend(["-D", f"html_theme={project.kebab_name}"])

            subprocess.run(command, check=True)
        return 0
