import contextlib
import errno
import os
import shutil
import stat
import tempfile
from pathlib import Path
from types import TracebackType
from typing import Any, Callable, Generator, Tuple, Type

import click
import pytest
from click.testing import CliRunner


# --------------------------------------------------------------------------------------
# Fixtures
@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def cli() -> click.Group:
    from sphinx_theme_builder._internal.cli import compose_command_line

    return compose_command_line()


# --------------------------------------------------------------------------------------
# Work around https://github.com/pytest-dev/pytest/issues/7821
@contextlib.contextmanager
def tmpdir() -> Generator[Path, None, None]:
    """Contextmanager to create a temporary directory.  It will be cleaned up
    afterwards.
    """
    tempdir = tempfile.mkdtemp()
    try:
        yield Path(tempdir)
    finally:
        rmtree(tempdir)


def rmtree(path: str) -> None:
    """On windows, rmtree fails for readonly dirs."""

    def handle_remove_readonly(
        func: Callable[..., Any],
        path: str,
        exc: Tuple[Type[OSError], OSError, TracebackType],
    ) -> None:
        excvalue = exc[1]
        if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
            for p in (path, os.path.dirname(path)):
                os.chmod(p, os.stat(p).st_mode | stat.S_IWUSR)
            func(path)
        else:
            raise  # noqa

    shutil.rmtree(path, ignore_errors=False, onerror=handle_remove_readonly)


# --------------------------------------------------------------------------------------
