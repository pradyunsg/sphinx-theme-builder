"""Development automation."""

import glob
import os
import shutil
import tempfile

import nox

PACKAGE_NAME = "sphinx_theme_builder"
nox.options.sessions = ["lint", "docs"]


#
# Development Sessions
#
@nox.session(name="docs-live", reuse_venv=True)
def docs_live(session):
    session.install("-e", ".[cli]")
    session.install("-r", "docs/requirements.txt")
    session.install("sphinx-autobuild")

    with tempfile.TemporaryDirectory() as destination:
        session.run(
            "sphinx-autobuild",
            # for sphinx-autobuild
            "--watch=README.md",
            "--port=0",
            "--open-browser",
            # for sphinx
            "-b=dirhtml",
            "-a",
            "docs/",
            destination,
        )


@nox.session(reuse_venv=True)
def docs(session):
    session.install("-e", ".[cli]")
    session.install("-r", "docs/requirements.txt")

    # Generate documentation into `build/docs`
    session.run(
        "sphinx-build",
        "-b",
        "dirhtml",
        "-W",
        "--keep-going",
        "-v",
        "docs/",
        "build/docs",
    )


@nox.session(reuse_venv=True)
def lint(session: nox.Session):
    session.install("pre-commit")

    args = list(session.posargs)
    args.append("--all-files")
    if "CI" in os.environ:
        args.append("--show-diff-on-failure")

    session.run("pre-commit", "run", *args)
    session.notify("mypy")


@nox.session
def typecheck(session: nox.Session):
    session.install(".[cli]", "mypy", "-r", "tests/requirements.txt")
    session.run("mypy", "src", "tests", "--strict")


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"], reuse_venv=True)
def test(session):
    if os.environ.get("CI"):
        session.install(".[cli]")
    else:
        session.install("-e", ".[cli]")

    session.install("-r", "tests/requirements.txt")

    args = session.posargs or (
        "--cov=sphinx_theme_builder",
        "--cov-branch",
        "--cov-report=term-missing",
        "--cov-report=html",
    )

    session.run(
        "pytest",
        "--pspec",
        *args,
    )


def get_release_versions(version_file):
    marker = "__version__ = "

    with open(version_file) as f:
        for line in f:
            if line.startswith(marker):
                version = line[len(marker) + 1 : -2]
                current_version, current_dev_number = version.split("dev")
                break
        else:
            raise RuntimeError("Could not find current version.")

    next_dev_number = int(current_dev_number) + 1
    release_version = f"{current_version}b{next_dev_number}"
    next_version = f"{current_version}dev{next_dev_number}"

    return release_version, next_version


@nox.session
def release(session):
    version_file = f"src/{PACKAGE_NAME}/__init__.py"
    allowed_upstreams = [
        f"git@github.com:pradyunsg/{PACKAGE_NAME.replace('_', '-')}.git"
    ]

    release_version, next_version = get_release_versions(version_file)

    session.install("build", "twine", "release-helper")

    # Sanity Checks
    session.run("release-helper", "version-check-validity", release_version)
    session.run("release-helper", "version-check-validity", next_version)
    session.run("release-helper", "directory-check-empty", "dist")

    session.run("release-helper", "git-check-branch", "main")
    session.run("release-helper", "git-check-clean")
    session.run("release-helper", "git-check-tag", release_version, "--does-not-exist")
    session.run("release-helper", "git-check-remote", "origin", *allowed_upstreams)

    # Prepare release commit
    session.run("release-helper", "version-bump", version_file, release_version)
    session.run("git", "add", version_file, external=True)

    session.run(
        "git", "commit", "-m", f"Prepare release: {release_version}", external=True
    )

    # Build the package
    if os.path.exists("build"):
        shutil.rmtree("build")
    session.run("python", "-m", "build")
    session.run("twine", "check", *glob.glob("dist/*"))

    # Tag the commit
    session.run(
        # fmt: off
        "git", "tag", release_version, "-m", f"Release {release_version}", "-s",
        external=True,
        # fmt: on
    )

    # Prepare back-to-development commit
    session.run("release-helper", "version-bump", version_file, next_version)
    session.run("git", "add", version_file, external=True)
    session.run("git", "commit", "-m", "Back to development", external=True)

    # Push the commits and tag.
    session.run("git", "push", "origin", "main", release_version, external=True)

    # Upload the distributions.
    session.run("twine", "upload", *glob.glob("dist/*"))
