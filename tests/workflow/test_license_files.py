import subprocess
import tarfile
import textwrap
from email.parser import BytesParser
from pathlib import Path

import pytest

from sphinx_theme_builder import build_sdist, prepare_metadata_for_build_wheel

LICENSES = {
    "LICENSE": b"project license",
    "vendor/licenses/LICENSE": b"vendor license",
    ".notices/NOTICE": b"third-party notice",
}


@pytest.fixture
def theme(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "theme"
    package = root / "src" / "magic"
    (package / "theme" / "magic").mkdir(parents=True)
    (package / "__init__.py").touch()
    (package / "theme" / "magic" / "theme.conf").write_text(
        "[theme]\nstylesheet = styles/magic.css\n"
    )
    (package / "assets" / "scripts").mkdir(parents=True)
    (package / "assets" / "styles").mkdir()
    (root / "pyproject.toml").write_text(
        textwrap.dedent(
            """\
            [project]
            name = "magic"
            version = "1.0"
            license-files = ["LICENSE", "vendor/licenses/*", ".notices/NOTICE"]

            [tool.sphinx-theme-builder]
            node-version = "16.13.0"
            """
        )
    )
    for name, content in LICENSES.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    monkeypatch.chdir(root)
    return root


def test_prepared_metadata_preserves_license_paths(theme: Path, tmp_path: Path) -> None:
    metadata = tmp_path / prepare_metadata_for_build_wheel(str(tmp_path))
    headers = BytesParser().parsebytes((metadata / "METADATA").read_bytes())
    assert set(headers.get_all("License-File", [])) == LICENSES.keys()
    for name, content in LICENSES.items():
        assert (metadata / "licenses" / name).read_bytes() == content


def test_sdist_includes_declared_untracked_licenses(
    theme: Path, tmp_path: Path
) -> None:
    subprocess.run(["git", "init", "-q"], check=True)
    subprocess.run(["git", "add", "src", "pyproject.toml", "LICENSE"], check=True)
    (theme / "vendor" / "unrelated.txt").touch()
    (theme / ".notices" / "unrelated.txt").touch()

    with tarfile.open(tmp_path / build_sdist(str(tmp_path))) as archive:
        for name, content in LICENSES.items():
            member = archive.extractfile(f"magic-1.0/{name}")
            assert member is not None
            assert member.read() == content
        assert "magic-1.0/vendor/unrelated.txt" not in archive.getnames()
        assert "magic-1.0/.notices/unrelated.txt" not in archive.getnames()
