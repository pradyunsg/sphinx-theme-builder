import shutil
import subprocess
import tempfile
from pathlib import Path

import click

from ..errors import STBError
from ..ui import log


class FetchSampleDocsCommand:
    """Fetch sphinx-themes.org's sample documentation set for this project.

    This command replaces the contents of the destination folder with the sample
    documentation set.

    This needs `git` on PATH, configured for read access to the repository.
    """

    interface: list[click.Parameter] = [
        click.Argument(
            ["destination_folder"],
            required=True,
            type=click.Path(
                exists=False,
                file_okay=False,
                dir_okay=True,
                writable=True,
                path_type=Path,
            ),
        ),
        click.Option(
            ["--ref", "git_ref"],
            required=False,
            type=str,
            help="Override the git reference to fetch from.",
        ),
    ]

    def run(
        self,
        *,
        destination_folder: Path,
        git_ref: str | None,
    ) -> int:
        repository = "https://github.com/sphinx-themes/sphinx-themes.org.git"
        directory = "sample-docs/"

        log(f"Fetching [green bold]{directory}[/] from [green bold]{repository}[/].")
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            self.fetch_and_populate(
                clone_path=tmp_path,
                repository=repository,
                directory=directory,
                git_ref=git_ref,
                destination_folder=destination_folder,
            )

        log("All done!")
        return 0

    def fetch_and_populate(
        self,
        *,
        clone_path: Path,
        repository: str,
        directory: str,
        git_ref: str | None,
        destination_folder: Path,
    ) -> None:
        try:
            self.clone_git_subfolder(
                clone_path=clone_path,
                repository=repository,
                directory=directory,
                git_ref=git_ref,
            )
        except subprocess.CalledProcessError as e:
            raise STBError(
                code="fetch-sample-docs-clone-failed",
                message="Failed to fetch the repository using git.",
                causes=[f"git exited with non-zero status code: {e.returncode}"],
                hint_stmt="The git output is available above.",
            ) from e

        if not (clone_path / directory).is_dir():
            raise STBError(
                code="fetch-sample-docs-missing-directory",
                message="The specified directory does not exist in the repository.",
                causes=[
                    f"Repository: {repository} (ref: {git_ref or 'default branch'})",
                    f"Subfolder under repository: {directory}",
                ],
                note_stmt="This can only happen if the repository structure changed.",
                hint_stmt=f"Use an older `--ref` where {directory} was present.",
            )

        try:
            self.replace_destination_folder(
                clone_path=clone_path,
                directory=directory,
                destination_folder=destination_folder,
            )
        except OSError as e:
            raise STBError(
                code="fetch-sample-docs-copy-failed",
                message="Failed to write the sample docs to the destination folder.",
                causes=[
                    f"Encountered {e!r}",
                    f"Relevant file(s): {', '.join(filter(None, [e.filename, e.filename2])) or '(none)'}",
                ],
                hint_stmt="Check filesystem permissions and available disk space for the destination folder.",
            ) from e

    def clone_git_subfolder(
        self,
        *,
        clone_path: Path,
        repository: str,
        directory: str,
        git_ref: str | None,
    ) -> None:
        """Clone the given repository's directory into the destination folder."""
        # https://stackoverflow.com/a/52269934
        clone_args = [
            "--depth=1",  # shallow
            "--filter=tree:0",  # treeless
            "--no-checkout",
            "--single-branch",
        ]
        if git_ref is not None:
            clone_args.extend(["--revision", git_ref])

        human_ref = git_ref or "default branch"
        log(
            "[magenta]$[/]",
            "[blue]git clone ...[/]",
            f"ref=[magenta]{human_ref}[/]",
            "\\[shallow, treeless, no checkout]",
        )
        subprocess.run(
            ["git", "clone", *clone_args, repository, clone_path], cwd=None, check=True
        )

        log("[magenta]$[/]", "[blue]git show HEAD[/]")
        subprocess.run(
            ["git", "show", "HEAD", "--oneline", "--no-patch", "--no-abbrev-commit"],
            cwd=clone_path,
            check=True,
        )

        log(
            "[magenta]$[/]",
            f"[blue]git sparse-checkout ...[/] directory=[magenta]{directory}[/]",
        )
        subprocess.run(
            ["git", "sparse-checkout", "set", "--no-cone", directory],
            cwd=clone_path,
            check=True,
        )
        subprocess.run(
            ["git", "checkout"],
            cwd=clone_path,
            check=True,
        )

    def replace_destination_folder(
        self,
        *,
        clone_path: Path,
        directory: str,
        destination_folder: Path,
    ) -> None:
        """Replace the contents of destination_folder with clone_path/directory."""
        log(
            f"Moving [magenta]\\[local clone]/{directory}[/]",
            f"to [yellow]{destination_folder}[/].",
        )
        if destination_folder.exists():
            shutil.rmtree(destination_folder)

        destination_folder.parent.mkdir(parents=True, exist_ok=True)
        source_folder = clone_path / directory
        shutil.copytree(source_folder, destination_folder)
