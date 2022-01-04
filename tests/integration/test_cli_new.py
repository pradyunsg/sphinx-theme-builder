import subprocess
import sys
from pathlib import Path
from unittest import mock

from click import Group
from click.testing import CliRunner

from sphinx_theme_builder._internal.cli.new import _TEMPLATE_URL
from sphinx_theme_builder._internal.errors import DiagnosticError


class TestNewCommand:
    """`stb new`"""

    def test_aborts_when_setup_py_exists(self, runner: CliRunner, cli: Group) -> None:
        with runner.isolated_filesystem() as directory:
            (Path(directory) / "setup.py").write_text("")

            with mock.patch("subprocess.run") as mocked_run:
                process = runner.invoke(cli, ["new", directory])

        assert mocked_run.call_count == 0
        assert process.exit_code == 1, process

    def test_aborts_when_pyproject_toml_exists(
        self, runner: CliRunner, cli: Group
    ) -> None:
        with runner.isolated_filesystem() as directory:
            (Path(directory) / "pyproject.toml").write_text("")

            with mock.patch("subprocess.run") as mocked_run:
                process = runner.invoke(cli, ["new", directory])

        assert mocked_run.call_count == 0
        assert process.exit_code == 1, process

    def test_calls_cookiecutter(self, runner: CliRunner, cli: Group) -> None:
        with runner.isolated_filesystem() as directory:
            with mock.patch("subprocess.run") as mocked_run:
                process = runner.invoke(cli, ["new", directory])

        assert process.exit_code == 0, process
        assert mocked_run.call_count == 1
        assert mocked_run.call_args == mock.call(
            [sys.executable, "-m", "cookiecutter", "-o", directory, _TEMPLATE_URL],
            check=True,
        )

    def test_cookiecutter_failure(self, runner: CliRunner, cli: Group) -> None:
        with runner.isolated_filesystem() as directory:
            with mock.patch("subprocess.run") as mocked_run:
                mocked_run.side_effect = subprocess.CalledProcessError(
                    returncode=2, cmd="placeholder"
                )
                process = runner.invoke(cli, ["new", directory])

        assert mocked_run.call_count == 1
        assert mocked_run.call_args == mock.call(
            [sys.executable, "-m", "cookiecutter", "-o", directory, _TEMPLATE_URL],
            check=True,
        )

        assert process.exit_code == 1, process
        assert isinstance(process.exception, DiagnosticError)
