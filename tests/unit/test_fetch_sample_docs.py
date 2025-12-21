import subprocess
from pathlib import Path
from unittest import mock

import pytest

from sphinx_theme_builder._internal.cli.fetch_sample_docs import (
    FetchSampleDocsCommand,
)
from sphinx_theme_builder._internal.errors import STBError


@mock.patch("subprocess.run")
def test_clone_git_subfolder_calls_git_commands(
    mock_run: mock.MagicMock, tmp_path: Path
) -> None:
    # GIVEN
    cmd = FetchSampleDocsCommand()

    # WHEN
    cmd.clone_git_subfolder(
        clone_path=tmp_path,
        repository="https://example.org/repo.git",
        directory="sample-docs/",
        git_ref=None,
    )

    # THEN
    assert mock_run.mock_calls == [
        mock.call(
            [
                "git",
                "clone",
                "--depth=1",
                "--filter=tree:0",
                "--no-checkout",
                "--single-branch",
                "https://example.org/repo.git",
                tmp_path,
            ],
            cwd=None,
            check=True,
        ),
        mock.call(
            ["git", "show", "HEAD", "--oneline", "--no-patch", "--no-abbrev-commit"],
            cwd=tmp_path,
            check=True,
        ),
        mock.call(
            ["git", "sparse-checkout", "set", "--no-cone", "sample-docs/"],
            cwd=tmp_path,
            check=True,
        ),
        mock.call(
            ["git", "checkout"],
            cwd=tmp_path,
            check=True,
        ),
    ]


@mock.patch("subprocess.run")
def test_clone_git_subfolder_with_ref_includes_revision(
    mock_run: mock.MagicMock, tmp_path: Path
) -> None:
    # GIVEN
    cmd = FetchSampleDocsCommand()

    # WHEN
    cmd.clone_git_subfolder(
        clone_path=tmp_path,
        repository="https://example.org/repo.git",
        directory="sample-docs/",
        git_ref="feature/thing",
    )

    # THEN
    assert mock_run.mock_calls == [
        mock.call(
            [
                "git",
                "clone",
                "--depth=1",
                "--filter=tree:0",
                "--no-checkout",
                "--single-branch",
                "--revision",
                "feature/thing",
                "https://example.org/repo.git",
                tmp_path,
            ],
            cwd=None,
            check=True,
        ),
        mock.call(
            ["git", "show", "HEAD", "--oneline", "--no-patch", "--no-abbrev-commit"],
            cwd=tmp_path,
            check=True,
        ),
        mock.call(
            ["git", "sparse-checkout", "set", "--no-cone", "sample-docs/"],
            cwd=tmp_path,
            check=True,
        ),
        mock.call(
            ["git", "checkout"],
            cwd=tmp_path,
            check=True,
        ),
    ]


def test_fetch_and_populate_clone_failure_raises_STBError(tmp_path: Path) -> None:
    # GIVEN
    cmd = FetchSampleDocsCommand()
    repository = "https://example.org/repo.git"
    directory = "sample-docs/"

    cmd.clone_git_subfolder = mock.MagicMock(  # type: ignore
        side_effect=subprocess.CalledProcessError(returncode=2, cmd=["boop"])
    )

    # WHEN
    with pytest.raises(STBError) as ctx:
        cmd.fetch_and_populate(
            clone_path=tmp_path / "clone",
            repository=repository,
            directory=directory,
            git_ref=None,
            destination_folder=tmp_path / "dest",
        )

    # THEN
    assert ctx.value.code == "fetch-sample-docs-clone-failed"
    assert ctx.value.causes == ["git exited with non-zero status code: 2"]


def test_fetch_and_populate_missing_directory_raises_STBError(tmp_path: Path) -> None:
    # GIVEN
    cmd = FetchSampleDocsCommand()
    clone_path = tmp_path / "clone"
    clone_path.mkdir()

    # WHEN
    with mock.patch.object(cmd, "clone_git_subfolder"):
        with pytest.raises(STBError) as ctx:
            cmd.fetch_and_populate(
                clone_path=clone_path,
                repository="https://example.org/repo.git",
                directory="sample-docs/",
                git_ref=None,
                destination_folder=tmp_path / "dest",
            )

    # THEN
    assert ctx.value.code == "fetch-sample-docs-missing-directory"
    assert ctx.value.causes == [
        "Repository: https://example.org/repo.git (ref: default branch)",
        "Subfolder under repository: sample-docs/",
    ]


def test_fetch_and_populate_copy_failure_raises_STBError(tmp_path: Path) -> None:
    # GIVEN
    cmd = FetchSampleDocsCommand()
    clone_path = tmp_path / "clone"
    dest_path = tmp_path / "dest"
    (clone_path / "sample-docs").mkdir(parents=True)

    cmd.replace_destination_folder = mock.MagicMock(side_effect=OSError("BOOM!"))  # type: ignore
    cmd.clone_git_subfolder = mock.MagicMock()  # type: ignore

    # WHEN
    with pytest.raises(STBError) as ctx:
        cmd.fetch_and_populate(
            clone_path=clone_path,
            repository="https://example.org/repo.git",
            directory="sample-docs/",
            git_ref=None,
            destination_folder=dest_path,
        )

    # THEN
    assert ctx.value.code == "fetch-sample-docs-copy-failed"
    assert ctx.value.causes == [
        "Encountered OSError('BOOM!')",
        "Relevant file(s): (none)",
    ]


def test_replace_destination_folder_replaces_existing(tmp_path: Path) -> None:
    # GIVEN
    cmd = FetchSampleDocsCommand()
    clone_path = tmp_path / "clone"
    (clone_path / "sample-docs").mkdir(parents=True)
    (clone_path / "sample-docs" / "index.rst").write_text("hello")

    dest = tmp_path / "out" / "dest"
    dest.mkdir(parents=True)
    (dest / "old.txt").write_text("old")

    # WHEN
    cmd.replace_destination_folder(
        clone_path=clone_path, directory="sample-docs/", destination_folder=dest
    )

    # THEN
    assert (dest / "index.rst").exists()
    assert not (dest / "old.txt").exists()


def test_replace_destination_folder_creates_nonexistent(tmp_path: Path) -> None:
    # GIVEN
    cmd = FetchSampleDocsCommand()
    clone_path = tmp_path / "clone"
    (clone_path / "sample-docs").mkdir(parents=True)
    (clone_path / "sample-docs" / "index.rst").write_text("hello")

    dest = tmp_path / "out" / "dest"

    # WHEN
    cmd.replace_destination_folder(
        clone_path=clone_path, directory="sample-docs/", destination_folder=dest
    )

    # THEN
    assert (dest / "index.rst").exists()


def test_run_uses_tempdir_and_returns_zero(tmp_path: Path) -> None:
    # GIVEN
    cmd = FetchSampleDocsCommand()

    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()

    tmpcm = mock.MagicMock()
    tmpcm.__enter__.return_value = str(tmpdir)
    tmpcm.__exit__.return_value = False

    mock_fetch_and_populate = mock.MagicMock()
    cmd.fetch_and_populate = mock_fetch_and_populate  # type: ignore

    # WHEN
    with mock.patch("tempfile.TemporaryDirectory", return_value=tmpcm):
        returncode = cmd.run(destination_folder=tmp_path / "dest", git_ref="main")

    # THEN
    assert returncode == 0
    mock_fetch_and_populate.assert_called_once_with(
        clone_path=tmpdir,
        repository="https://github.com/sphinx-themes/sphinx-themes.org.git",
        directory="sample-docs/",
        git_ref="main",
        destination_folder=tmp_path / "dest",
    )
