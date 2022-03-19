"""A tool for authoring Sphinx themes with a simple (opinionated) workflow.

This module also serves as the public PEP 517 API for this project.
"""

__version__ = "0.2.0a14"

import contextlib
import sys
import tempfile
from pathlib import Path
from typing import Dict, Iterator, Optional

import rich

from ._internal.distributions import generate_metadata as _generate_metadata
from ._internal.distributions import generate_source_distribution as _generate_sdist
from ._internal.distributions import generate_wheel_distribution as _generate_wheel
from ._internal.errors import DiagnosticError
from ._internal.project import Project


@contextlib.contextmanager
def _ensure_has_metadata(
    project: Project, metadata_directory: Optional[str]
) -> Iterator[Path]:
    """Ensure that the body of a with statement, is executed with metadata generated."""
    if metadata_directory is not None:
        yield Path(metadata_directory)
    else:
        # The build frontend didn't generate the metadata. Generate it in a temporary
        # directory, and provide that. Cleans up when the context is exited.
        with tempfile.TemporaryDirectory() as dirname:
            metadata_dirname = Path(dirname)
            metadata_basename = _generate_metadata(
                project,
                destination=Path(dirname),
            )
            yield metadata_dirname / metadata_basename


@contextlib.contextmanager
def _clean_error_presentation() -> Iterator[None]:
    try:
        yield
    except DiagnosticError as error:
        rich.get_console().print(error, soft_wrap=True)
        sys.exit(1)


#
# Source Distributions
#
def build_sdist(
    sdist_directory: str,
    config_settings: Optional[Dict[str, str]] = None,
) -> str:
    """Generate a source distribution and place it into `sdist_directory`.

    https://www.python.org/dev/peps/pep-0517/#build-sdist
    """
    with _clean_error_presentation():
        project = Project.from_cwd()
        return _generate_sdist(project, destination=Path(sdist_directory))


#
# Wheel Distributions
#
def prepare_metadata_for_build_wheel(
    metadata_directory: str,
    config_settings: Optional[Dict[str, str]] = None,
) -> str:
    """Generate the metadata (.dist-info) and place it in `metadata_directory`.

    https://www.python.org/dev/peps/pep-0517/#prepare-metadata-for-build-wheel
    """
    with _clean_error_presentation():
        project = Project.from_cwd()
        return _generate_metadata(project, destination=Path(metadata_directory))


def build_wheel(
    wheel_directory: str,
    config_settings: Optional[Dict[str, str]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    """Generate a wheel distribution and place it into `wheel_directory`.

    https://www.python.org/dev/peps/pep-0517/#build-wheel
    """
    with _clean_error_presentation():
        project = Project.from_cwd()
        with _ensure_has_metadata(project, metadata_directory) as metadata_path:
            return _generate_wheel(
                project,
                destination=Path(wheel_directory),
                metadata_directory=metadata_path,
                editable=False,
            )


#
# Editable installs
#
prepare_metadata_for_build_editable = prepare_metadata_for_build_wheel


def build_editable(
    wheel_directory: str,
    config_settings: Optional[Dict[str, str]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    """Generate an editable wheel distribution and place it into `wheel_directory`.

    https://www.python.org/dev/peps/pep-0660/#build-editable
    """
    with _clean_error_presentation():
        project = Project.from_cwd()
        with _ensure_has_metadata(project, metadata_directory) as metadata_path:
            return _generate_wheel(
                project,
                destination=Path(wheel_directory),
                metadata_directory=metadata_path,
                editable=True,
            )
