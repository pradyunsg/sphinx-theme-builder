import sys
from typing import Any, Dict, List, Optional, Protocol, Type

import rich

from ..errors import DiagnosticError
from ..ui import log

try:
    import build  # noqa
    import click
    import sphinx_autobuild  # type: ignore  # noqa
except ImportError as import_error:
    error = DiagnosticError(
        reference="missing-command-line-dependencies",
        message=(
            "Could not import a package that is required for the `stb` command line."
        ),
        context=str(import_error),
        note_stmt=(
            "The optional [blue]cli[/] dependencies of this package are missing."
        ),
        hint_stmt=(
            "During installation, make sure to include the `\\[cli]`. For example:\n"
            'pip install "sphinx-theme-builder\\[cli]"'
        ),
    )
    rich.print(error, file=sys.stderr)
    sys.exit(1)


class Command(Protocol):
    interface: List[click.Parameter]

    def run(self, **kwargs: Dict[str, Any]) -> int:
        ...


def create_click_command(cls: Type[Command]) -> click.Command:
    # Use the class docstring as the help string
    help_string = cls.__doc__
    # Infer the name, from the known context.
    name = cls.__name__[: -len("Command")].lower()

    # Double check that things are named correctly.
    assert name.capitalize() + "Command" == cls.__name__
    assert name == cls.__module__.split(".")[-1]

    command = click.Command(
        name=name,
        help=help_string,
        params=cls.interface,
        callback=lambda **kwargs: cls().run(**kwargs),
    )
    return command


def compose_command_line() -> click.Group:
    from .compile import CompileCommand
    from .new import NewCommand
    from .package import PackageCommand
    from .serve import ServeCommand

    command_classes: List[Type[Command]] = [
        CompileCommand,  # type: ignore
        NewCommand,  # type: ignore
        PackageCommand,  # type: ignore
        ServeCommand,  # type: ignore
    ]

    # Convert our commands into click objects.
    click_commands = [create_click_command(cls) for cls in command_classes]

    # Create the main click interface.
    cli = click.Group(
        name="stb",
        help="sphinx-theme-builder helps make it easier to write sphinx themes.",
        commands={command.name: command for command in click_commands},  # type: ignore
    )
    return cli


def main(args: Optional[List[str]] = None) -> None:
    """The entrypoint for command line stuff."""
    cli = compose_command_line()
    try:
        cli(args=args)
    except DiagnosticError as error:
        rich.get_console().print(error)
        sys.exit(1)
    except Exception:
        console = rich.get_console()
        console.print_exception(show_locals=True)
        log(
            "A fatal error occured. If the above error message is unclear, please file "
            "an issue against the project."
        )
        sys.exit(2)
