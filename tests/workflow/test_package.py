"""Overall workflow tests for `stb package`."""

from click import Group
from click.testing import CliRunner


class TestPackageCommand:
    def test_help(self, runner: CliRunner, cli: Group) -> None:
        process = runner.invoke(cli, ["package", "--help"])

        assert process.exit_code == 0, process.stdout
        assert process.stdout
