from unittest import mock

from click import Group
from click.testing import CliRunner


class TestCompileCommand:
    """`stb compile`"""

    def test_calls_generate_assets(self, runner: CliRunner, cli: Group) -> None:
        with (
            mock.patch(
                "sphinx_theme_builder._internal.cli.compile.generate_assets"
            ) as mocked_generate_assets,
            mock.patch(
                "sphinx_theme_builder._internal.cli.compile.Project"
            ) as mocked_project,
        ):
            with runner.isolated_filesystem():
                process = runner.invoke(cli, ["compile"])

        assert process.exit_code == 0, process

        mocked_generate_assets.assert_has_calls(
            [
                mock.call(mocked_project.from_cwd(), production=False),
            ]
        )

    def test_calls_generate_assets_in_production(
        self, runner: CliRunner, cli: Group
    ) -> None:
        with (
            mock.patch(
                "sphinx_theme_builder._internal.cli.compile.generate_assets"
            ) as mocked_generate_assets,
            mock.patch(
                "sphinx_theme_builder._internal.cli.compile.Project"
            ) as mocked_project,
        ):
            with runner.isolated_filesystem():
                process = runner.invoke(cli, ["compile", "--production"])

        assert process.exit_code == 0, process

        mocked_generate_assets.assert_has_calls(
            [
                mock.call(mocked_project.from_cwd(), production=True),
            ]
        )
