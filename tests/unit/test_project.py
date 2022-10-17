import sys
import textwrap
from pathlib import Path
from typing import Any
from unittest import mock

import pytest
from packaging.version import Version

from sphinx_theme_builder._internal.project import (
    ImproperProjectMetadata,
    InvalidProjectStructure,
    Project,
    read_toml_file,
)


@mock.patch(f"{'tomllib' if sys.version_info > (3, 11) else 'tomli'}.load")
def test_read_toml_file(patched_load: mock.Mock, tmp_path: Path) -> None:
    # GIVEN
    file = tmp_path / "foo.toml"
    file.write_text("")

    # WHEN
    read_toml_file(file)

    # THEN
    patched_load.assert_called_once()
    assert patched_load.call_args[0][0].name == str(file)


class TestProjectFromPath:
    def test_works_on_valid_pyproject(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text(
            textwrap.dedent(
                """
                [project]
                name = 'magic-project'
                version = '1.0'
                license = { text = "MIT" }

                [tool.sphinx-theme-builder]
                node-version = "16.13.0"
                """
            )
        )
        (tmp_path / "src" / "magic_project").mkdir(parents=True)
        (tmp_path / "src" / "magic_project" / "__init__.py").write_text("")

        # WHEN
        project = Project.from_path(tmp_path)

        # THEN
        assert project.snake_name == "magic_project"
        assert project.kebab_name == "magic-project"
        assert project.location == tmp_path

        assert project.metadata
        assert project.metadata.version == Version("1.0")

        assert project.python_package_path == tmp_path / "src" / "magic_project"
        assert project.theme_path == (
            tmp_path / "src" / "magic_project" / "theme" / "magic-project"
        )
        assert project.theme_conf_path == (
            tmp_path
            / "src"
            / "magic_project"
            / "theme"
            / "magic-project"
            / "theme.conf"
        )
        assert project.theme_static_path == (
            tmp_path / "src" / "magic_project" / "theme" / "magic-project" / "static"
        )
        assert project.output_script_path == (
            project.theme_static_path / "scripts" / "magic-project.js"
        )
        assert project.output_stylesheet_path == (
            project.theme_static_path / "styles" / "magic-project.css"
        )

        assert project.assets_path == tmp_path / "src" / "magic_project" / "assets"
        assert project.input_stylesheets_path == (
            tmp_path / "src" / "magic_project" / "assets" / "styles"
        )
        assert project.input_scripts_path == (
            tmp_path / "src" / "magic_project" / "assets" / "scripts"
        )

    def test_rejects_without_pyproject_toml(self, tmp_path: Path) -> None:
        # GIVEN
        # an empty directory

        # WHEN
        with pytest.raises(InvalidProjectStructure) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert "Could not find a `pyproject.toml`" in error.message
        assert error.context
        assert str(tmp_path) in error.context
        assert error.reference == "pyproject-missing"

    def test_rejects_on_invalid_pyproject_toml(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text("key = value")

        # WHEN
        with pytest.raises(ImproperProjectMetadata) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert "Could not parse `pyproject.toml`" in error.message
        assert error.context
        assert str(tmp_path) in error.context
        assert "pyproject.toml" in error.context
        assert "line 1, column 7" in error.context
        assert error.reference == "pyproject-could-not-parse"

    def test_rejects_without_project_table(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text("key = 1")

        # WHEN
        with pytest.raises(ImproperProjectMetadata) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert "Could not find [project] table" in error.message
        assert error.context
        assert str(tmp_path) in error.context
        assert "pyproject.toml" in error.context
        assert error.reference == "pyproject-no-project-table"

    def test_rejects_without_name(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text("[project]\nkey = 1")

        # WHEN
        with pytest.raises(ImproperProjectMetadata) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert "Could not find `name`" in error.message
        assert "[project] table" in error.message
        assert error.context
        assert "pyproject.toml" in error.context
        assert error.reference == "pyproject-no-name-in-project-table"

    def test_rejects_non_canonical_names(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'MAGIC'")

        # WHEN
        with pytest.raises(ImproperProjectMetadata) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert (
            "Found non-canonical `name` declared in the [project] table"
            in error.message
        )
        assert error.context
        assert "pyproject.toml" in error.context
        assert error.reference == "pyproject-non-canonical-name"

    def test_works_with_proper_static_version(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text(
            textwrap.dedent(
                """
                [project]
                name = "magic"
                version = "0.1.2"
                license = { text = "MIT" }

                [tool.sphinx-theme-builder]
                node-version = "16.13.0"
                """
            )
        )
        (tmp_path / "src" / "magic").mkdir(parents=True)
        (tmp_path / "src" / "magic" / "__init__.py").write_text("")

        # WHEN
        project = Project.from_path(tmp_path)

        # THEN
        assert project.metadata.version == Version("0.1.2")

    def test_works_with_proper_dynamic_version(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text(
            textwrap.dedent(
                """
                [project]
                name = "magic"
                dynamic = ["version"]
                license = { text = "MIT" }

                [tool.sphinx-theme-builder]
                node-version = "16.13.0"
                """
            )
        )
        (tmp_path / "src" / "magic").mkdir(parents=True)
        (tmp_path / "src" / "magic" / "__init__.py").write_text(
            textwrap.dedent(
                """
                version = "2.3.4"  # not really, we just ignore this.
                __version__ = "1.2.3"
                """
            )
        )

        # WHEN
        project = Project.from_path(tmp_path)

        # THEN
        assert project.metadata.version == Version("1.2.3")

    def test_rejects_when_no_version_is_declared(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text(
            textwrap.dedent(
                """
                [project]
                name = "magic"
                """
            )
        )
        (tmp_path / "src" / "magic").mkdir(parents=True)
        (tmp_path / "src" / "magic" / "__init__.py").write_text("")

        # WHEN
        with pytest.raises(InvalidProjectStructure) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert "No version declaration found for project." in error.message
        assert error.context
        assert "__init__.py" in error.context
        assert "pyproject.toml" in error.context
        assert error.hint_stmt
        assert "forget" in error.hint_stmt
        assert "?" in error.hint_stmt
        assert error.reference == "project-no-version-declaration"

    def test_rejects_when_no_python_file_is_available(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text(
            textwrap.dedent(
                """
                [project]
                name = "magic"
                version = "1.0.0"
                """
            )
        )

        # WHEN
        with pytest.raises(InvalidProjectStructure) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert "__init__.py is missing" in error.message
        assert error.context
        assert "project name is magic" in error.context
        assert error.reference == "project-init-missing"

    def test_rejects_with_double_declaration(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text(
            textwrap.dedent(
                """
                [project]
                name = "magic"
                version = "1.2.3"
                """
            )
        )
        (tmp_path / "src" / "magic").mkdir(parents=True)
        (tmp_path / "src" / "magic" / "__init__.py").write_text('__version__ = "2.3.4"')

        # WHEN
        with pytest.raises(InvalidProjectStructure) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert "Found version declaration in both" in error.message
        assert "pyproject.toml" in error.message
        assert "__init__.py" in error.message
        assert error.reference == "project-double-version-declaration"

    def test_rejects_dynamic_with_version_in_pyproject(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text(
            textwrap.dedent(
                """
                [project]
                name = "magic"
                version = "2.3.4"
                dynamic = ["version"]
                """
            )
        )
        (tmp_path / "src" / "magic").mkdir(parents=True)
        (tmp_path / "src" / "magic" / "__init__.py").write_text("")

        # WHEN
        with pytest.raises(ImproperProjectMetadata) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert "dynamic" in error.message
        assert "version" in error.message
        assert "pyproject.toml" in error.message
        assert error.context
        assert "2.3.4" in error.context
        assert error.hint_stmt
        assert "removing `version`" in error.hint_stmt
        assert error.reference == "project-improper-dynamic-version"

    def test_rejects_no_dynamic_with_version_in_python_file(
        self, tmp_path: Path
    ) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text(
            textwrap.dedent(
                """
                [project]
                name = "magic"
                """
            )
        )
        (tmp_path / "src" / "magic").mkdir(parents=True)
        (tmp_path / "src" / "magic" / "__init__.py").write_text('__version__ = "1.2.3"')

        # WHEN
        with pytest.raises(ImproperProjectMetadata) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert "Found version in `__init__.py`" in error.message
        assert '"version" in `project.dynamic' in error.message
        assert error.context
        assert "1.2.3" in error.context
        assert error.hint_stmt
        assert error.reference == "project-missing-dynamic-version"

    @pytest.mark.parametrize("value", [1, 1.0, []])
    def test_rejects_non_string_static_versions_toml(
        self, tmp_path: Path, value: Any
    ) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text(
            textwrap.dedent(
                f"""
                [project]
                name = "magic"
                version = {value}
                """
            )
        )
        (tmp_path / "src" / "magic").mkdir(parents=True)
        (tmp_path / "src" / "magic" / "__init__.py").write_text("")

        # WHEN
        with pytest.raises(ImproperProjectMetadata) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert "Expected " in error.message
        assert "a string" in error.message
        assert error.context
        assert f"Got {value}" in error.context
        assert f"{type(value)}" in error.context
        assert error.reference == "pyproject-invalid-version"

    def test_rejects_invalid_versions(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text(
            textwrap.dedent(
                """
                [project]
                name = "magic"
                version = "asdf"
                """
            )
        )
        (tmp_path / "src" / "magic").mkdir(parents=True)
        (tmp_path / "src" / "magic" / "__init__.py").write_text("")

        # WHEN
        with pytest.raises(ImproperProjectMetadata) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert "invalid version" in error.message
        assert "asdf" in error.message
        assert error.context
        assert "pyproject.toml" in error.context
        assert error.reference == "project-invalid-version"

    def test_rejects_invalid_python_files(self, tmp_path: Path) -> None:
        # GIVEN
        (tmp_path / "pyproject.toml").write_text(
            textwrap.dedent(
                """
                [project]
                name = "magic"
                dynamic = ["version"]
                """
            )
        )
        (tmp_path / "src" / "magic").mkdir(parents=True)
        (tmp_path / "src" / "magic" / "__init__.py").write_text(")")

        # WHEN
        with pytest.raises(InvalidProjectStructure) as ctx:
            Project.from_path(tmp_path)

        # THEN
        error = ctx.value
        assert "Could not parse" in error.message
        assert error.context
        assert "__init__.py" in error.context
        assert "SyntaxError" in error.context
        assert error.reference == "project-init-invalid-syntax"
