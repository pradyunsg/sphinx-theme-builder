"""Overall workflow tests for `stb`."""

from click import Group
from click.testing import CliRunner


class TestCLIRoot:
    def test_no_arguments(self, runner: CliRunner, cli: Group) -> None:
        process = runner.invoke(cli, [])

        assert process.exit_code == 0
        assert process.stdout

    def test_help(self, runner: CliRunner, cli: Group) -> None:
        process = runner.invoke(cli, ["--help"])

        assert process.exit_code == 0
        assert process.stdout

    def test_no_arguments_behaves_same_as_help(
        self, runner: CliRunner, cli: Group
    ) -> None:
        process_one = runner.invoke(cli, [])
        process_two = runner.invoke(cli, ["--help"])

        assert process_one.stdout == process_two.stdout
