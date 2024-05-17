"""NodeJS tooling orchestration.

Broadly, it has a `.nodeenv` created using the nodeenv package; and ensures that the
`node_modules` directory is kept in sync with the `package.json` file of the project.
"""

import os
import pathlib
import platform
import shlex
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, List, Optional
from unittest.mock import patch

from rich.markup import escape

from .errors import DiagnosticError
from .passthrough import passthrough_run
from .project import Project
from .ui import log

_NODEENV_DIR = ".nodeenv"
_BIN_DIR = "Scripts" if os.name == "nt" else "bin"


def _get_bool_env_var(name: str, *, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    if value.lower() in {"false", "0"}:
        return False
    if value.lower() in {"true", "1"}:
        return True
    raise DiagnosticError(
        reference="non-boolean-env-variable-value",
        message=f"The provided value for `{name}` is invalid.",
        context=f"{name}={escape(value)}",
        hint_stmt=f"Provide a boolean value for `{name}` (true, false, 1, 0).",
    )


def _resolve_executable_win_312(name: str, path: str) -> str | None:
    resolved_name = shutil.which(name, path=path)
    resolved_path = pathlib.Path(resolved_name)
    if resolved_path.suffix:
        return resolved_name

    try:
        extensions = os.environ.get("PATHEXT")
    except KeyError:
        return resolved_name

    for extension in extensions.split(";"):
        candidate_path = resolved_path.with_suffix(extension)
        if candidate_path.exists():
            return os.fsdecode(candidate_path)
    return resolved_name


def run_in(
    nodeenv: Path, args: List[str], *, production: bool = False, **kwargs: Any
) -> "Optional[subprocess.CompletedProcess[bytes]]":
    """Run a command, using a binary from `nodeenv`."""
    assert nodeenv.name == _NODEENV_DIR

    log(f"[magenta](nodeenv) $[/] [blue]{' '.join(args)}[/]")
    env = {
        "NPM_CONFIG_PREFIX": os.fsdecode(nodeenv),
        "npm_config_prefix": os.fsdecode(nodeenv),
        "NODE_PATH": os.fsdecode(nodeenv / "lib" / "node_modules"),
        "PATH": os.pathsep.join([os.fsdecode(nodeenv / _BIN_DIR), os.environ["PATH"]]),
        "NODE_ENV": "production" if production else "development",
    }

    # Fully qualify the first argument.
    # On Windows with Python 3.12.0, we need to handle modified behavior in which
    if ((3, 12, 0) <= sys.version_info < (3, 12, 1)) and platform.system() == "Windows":
        resolved_name = _resolve_executable_win_312(args[0], path=env["PATH"])
    else:
        resolved_name = shutil.which(args[0], path=env["PATH"])

    if resolved_name is None:
        raise FileNotFoundError(resolved_name)
    args[0] = resolved_name

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
    presentation = ["python", "-m", "nodeenv", *args]
    log(f"[magenta]$[/] [blue]{' '.join(presentation)}[/]")

    command = [
        sys.executable,
        "-c",
        textwrap.dedent(
            """
            import runpy
            import rich
            import rich.traceback
            import urllib.request

            rich.traceback.install(
                width=rich.get_console().width,
                show_locals=True,
                suppress=[runpy, urllib.request],
            )
            runpy.run_module("nodeenv", run_name="__main__", alter_sys=True)
            """
        ),
        "-v",
        *args,
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        raise DiagnosticError(
            reference="nodeenv-creation-failed",
            message="Failed to create a `nodeenv`",
            context="See above for failure output from the underlying tooling.",
            hint_stmt=(
                "A `urllib.error.HTTPError` indicates that the issue is "
                "related to the network or the availability of NodeJS release files. "
                "It may mean the node version that this tool is trying to fetch is no "
                "longer available, for example if there is no compatible NodeJS binary "
                "for the operating system."
            ),
        ) from error


def _should_use_system_node(node_version: str) -> bool:
    if not _get_bool_env_var("STB_USE_SYSTEM_NODE", default=False):
        return False

    if sys.platform == "win32":
        raise DiagnosticError(
            reference="can-not-use-system-node-on-windows",
            message="sphinx-theme-builder can not use the system node on Windows.",
            context="The underlying tooling (nodeenv) does not yet support this.",
            hint_stmt="Unset `STB_USE_SYSTEM_NODE`, which is currently set to 'true'",
        )
    return True


def _relaxed_version_check(expected: str, got: str) -> Optional[str]:
    """Perform a relaxed check of the failure mode.

    Returns None, if the versions match the relaxed check criterion.
    Returns a string, with the reason for the the version check failure.
    """
    assert expected.startswith("v"), expected
    assert got.startswith("v"), got

    expected_parts = expected[1:].split(".")[:2]
    got_parts = got[1:].split(".")[:2]

    assert len(expected_parts) == len(got_parts) == 2, f"{expected};{got}"

    if expected_parts[0] != got_parts[0]:
        return "Minor version does not match the value declared in the theme."
    if int(expected_parts[1]) < int(got_parts[1]):
        return "Minor version is lower than the value declared in the theme."
    return None


def ensure_version_matches(expected: str, got: str) -> None:
    """Ensure that the version of NodeJS matches the expected value.

    STB_RELAX_NODE_VERSION_CHECK can be used to relax the check, to only check the major
    and minor version.
    """
    if got == expected:
        return

    if not _get_bool_env_var("STB_RELAX_NODE_VERSION_CHECK", default=False):
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

    log("[yellow]#[/] The node version is not the expected one.")
    log("[yellow]#[/] The generated assets may be broken even if the build succeeds.")
    log("[yellow]#[/] Continuing anyway - `STB_RELAX_NODE_VERSION_CHECK` is truthy.")

    rejection_reason = _relaxed_version_check(expected, got)
    if rejection_reason is None:
        return

    raise DiagnosticError(
        reference="node-version-mismatch",
        message="The node version is not compatible with the expected version.",
        context=f"{rejection_reason}\nSee above for the expected and actual version.",
        hint_stmt=(
            "You need to use a compatible version of NodeJS to build the theme. "
        ),
    )


def create_nodeenv(nodeenv: Path, node_version: str) -> None:
    """Create a `nodeenv` for the theme."""
    log(
        "[yellow]#[/] [cyan]Generating new [magenta]nodeenv[/] with "
        f"NodeJS [green]{node_version}[/]!"
    )

    if _should_use_system_node(node_version=node_version):
        log("[yellow]#[/] Will use system nodeJS.")
        node_version = "system"

    envdir = os.fsdecode(nodeenv)
    # This next bit is borrowed from
    # https://github.com/pre-commit/pre-commit/blob/v2.16.0/pre_commit/languages/node.py
    if sys.platform == "win32":  # pragma: no cover
        envdir = "\\\\?\\" + os.path.normpath(envdir)

    _run_python_nodeenv(
        f"--node={node_version}",
        "--prebuilt",
        "--clean-src",
        envdir,
    )


def run_npm_build(nodeenv: Path, *, production: bool) -> None:
    try:
        run_in(nodeenv, ["npm", "run-script", "build"], production=production)
    except subprocess.CalledProcessError as error:
        raise DiagnosticError(
            reference="js-build-failed",
            message="The Javascript-based build pipeline failed.",
            context="See above for failure output from the underlying tooling.",
            hint_stmt=None,
        ) from error


def populate_npm_packages(nodeenv: Path, node_modules: Path) -> None:
    try:
        run_in(nodeenv, ["npm", "install", "--include=dev"])
    except FileNotFoundError as error:
        raise DiagnosticError(
            reference="nodeenv-unhealthy-npm-not-found",
            message="The `nodeenv` for this project is unhealthy.",
            context=str(error),
            hint_stmt=(
                f"Deleting the {_NODEENV_DIR} directory and trying again may work."
            ),
        ) from error
    except subprocess.CalledProcessError as error:
        raise DiagnosticError(
            reference="js-install-failed",
            message="Javascript dependency installation failed.",
            context="See above for failure output from the underlying tooling.",
            hint_stmt=None,
        ) from error

    if node_modules.is_dir():
        node_modules.touch()


def generate_assets(project: Project, *, production: bool) -> None:
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
    ensure_version_matches(expected, got)

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

    run_npm_build(nodeenv=nodeenv, production=production)

    log("[green]Done![/]")
