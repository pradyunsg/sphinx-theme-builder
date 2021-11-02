"""Overall workflow tests for `stb build`."""

from click import Group
from click.testing import CliRunner


class TestBuildCommand:
    def test_help(self, runner: CliRunner, cli: Group) -> None:
        process = runner.invoke(cli, ["build", "--help"])

        assert process.exit_code == 0
        assert process.stdout
