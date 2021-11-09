"""NodeJS tooling orchestration.

Broadly, it has a `.nodeenv` created using the nodeenv package; and ensures that the
`node_modules` directory is kept in sync with the `package.json` file of the project.
"""

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, List, Optional
from unittest.mock import patch

from .errors import DiagnosticError
from .passthrough import passthrough_run
from .project import Project
from .ui import log

_NODEENV_DIR = ".nodeenv"
_BIN_DIR = "Scripts" if os.name == "nt" else "bin"


def run_in(
    nodeenv: Path, args: List[str], **kwargs: Any
) -> "Optional[subprocess.CompletedProcess[bytes]]":
    """Run a command, using a binary from `nodeenv`."""
    assert nodeenv.name == _NODEENV_DIR

    log(f"[magenta](nodeenv) $[/] [blue]{_NODEENV_DIR}/{_BIN_DIR}/{' '.join(args)}[/]")
    env = {
        "NPM_CONFIG_PREFIX": os.fsdecode(nodeenv),
        "npm_config_prefix": os.fsdecode(nodeenv),
        "NODE_PATH": os.fsdecode(nodeenv / "lib" / "node_modules"),
        "PATH": os.pathsep.join([os.fsdecode(nodeenv / "bin"), os.environ["PATH"]]),
    }

    # Fully qualify the first argument.
    args[0] = os.fsdecode(nodeenv / "bin" / args[0])

    with patch.dict("os.environ", env):
        if not kwargs:
            returncode = passthrough_run(args)
            if returncode:
                cmd = " ".join(shlex.quote(arg) for arg in args)
                raise subprocess.CalledProcessError(returncode=returncode, cmd=cmd)
            return None
        else:
            return subprocess.run(args, check=True, **kwargs)


def _run_python_nodeenv(*args: str) -> None:
    command = [str(sys.executable), "-m", "nodeenv", *args]
    log(f"[magenta]$[/] [blue]python {' '.join(command[1:])}[/]")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        raise DiagnosticError(
            reference="nodeenv-creation-failed",
            message="Failed to create a `nodeenv`",
            context="See above for failure output from the underlying tooling.",
            hint_stmt=(
                "A `urllib.error.HTTPError` would indicate mean that the issue is "
                "related to the network, or the NodeJS servers, or the node version "
                "that this tool is trying to fetch is no longer available."
            ),
        ) from error


def _should_use_system_node(node_version: str) -> bool:
    process = subprocess.run(["node", "--version"], capture_output=True)
    if process.returncode:
        return False
    return process.stdout.decode().strip() == f"v{node_version}"


def create_nodeenv(nodeenv: Path, node_version: str) -> None:
    log(
        "[yellow]#[/] [cyan]Generating new [magenta]nodeenv[/] with "
        f"NodeJS [green]{node_version}[/]!"
    )

    if _should_use_system_node(node_version=node_version):
        log("[yellow]#[/] Will use system nodeJS, since version matches.")
        node_version = "system"

    _run_python_nodeenv(
        f"--node={node_version}",
        os.fsdecode(nodeenv),
    )


def run_npm_build(nodeenv: Path) -> None:
    try:
        run_in(nodeenv, ["npm", "run-script", "build"])
    except subprocess.CalledProcessError as error:
        raise DiagnosticError(
            reference="js-build-failed",
            message="The Javascript-based build pipeline failed.",
            context="See above for failure output from the underlying tooling.",
            hint_stmt=None,
        ) from error


def populate_npm_packages(nodeenv: Path, node_modules: Path) -> None:
    try:
        run_in(nodeenv, ["npm", "install", "--include=dev", "--no-save"])
    except subprocess.CalledProcessError as error:
        raise DiagnosticError(
            reference="js-install-failed",
            message="Javascript dependency installation failed.",
            context="See above for failure output from the underlying tooling.",
            hint_stmt=None,
        ) from error

    if node_modules.is_dir():
        node_modules.touch()


def generate_assets(project: Project) -> None:
    package_json = project.location / "package.json"
    nodeenv = project.location / _NODEENV_DIR
    node_modules = project.location / "node_modules"

    assert package_json.exists()

    created_new_nodeenv = False
    if not nodeenv.exists():
        log("[yellow]#[/] [magenta]nodeenv[cyan] does not exist.[/]")
        create_nodeenv(nodeenv, project.node_version)
        created_new_nodeenv = True

    # Checking the node version is a sanity check, and ensures that the environment is
    # "healthy".
    try:
        process = run_in(nodeenv, ["node", "--version"], stdout=subprocess.PIPE)
    except FileNotFoundError as error:
        raise DiagnosticError(
            reference="nodeenv-unhealthy-file-not-found",
            message="The `nodeenv` for this project is unhealthy.",
            context=str(error),
            hint_stmt=(
                f"Deleting the {_NODEENV_DIR} directory and trying again may work."
            ),
        ) from error
    except subprocess.CalledProcessError as error:
        raise DiagnosticError(
            reference="nodeenv-unhealthy-subprocess-failure",
            message="The `nodeenv` for this project is unhealthy.",
            context="See above for failure output from the underlying tooling.",
            hint_stmt=(
                f"Deleting the {_NODEENV_DIR} directory and trying again may work."
            ),
        ) from error

    # Present the `node --version` output to the user.
    assert process
    got = process.stdout.decode().strip()
    print(got)

    # Sanity-check the node version.
    expected = f"v{project.node_version}"
    if got != expected:
        raise DiagnosticError(
            reference="nodeenv-version-mismatch",
            message="The `nodeenv` for this project is unhealthy.",
            context=(
                "There is a mismatch between what is present in the environment "
                f"({got}) and the expected version of NodeJS ({expected})."
            ),
            hint_stmt=(
                f"Deleting the {_NODEENV_DIR} directory and trying again may work."
            ),
        )

    need_to_populate = False
    if created_new_nodeenv:
        need_to_populate = True
    elif not node_modules.exists():
        need_to_populate = True
    elif node_modules.stat().st_mtime < package_json.stat().st_mtime:
        log("[yellow]#[/] [cyan]Detected changes in [magenta]package.json[cyan].[/]")
        need_to_populate = True

    if need_to_populate:
        if node_modules.exists():
            log("[yellow]#[/] [cyan]Cleaning up [magenta]node_modules[cyan].[/]")
            try:
                shutil.rmtree(node_modules)
            except OSError as error:
                raise DiagnosticError(
                    reference="unable-to-cleanup-node-modules",
                    message="Could not remove node_modules directory.",
                    context=str(error),
                    hint_stmt=f"Deleting {node_modules} and trying again may work.",
                ) from error

        log("[yellow]#[/] [cyan]Installing NodeJS packages.[/]")
        populate_npm_packages(nodeenv, node_modules)

    run_npm_build(nodeenv=nodeenv)

    log("[green]Done![/]")
