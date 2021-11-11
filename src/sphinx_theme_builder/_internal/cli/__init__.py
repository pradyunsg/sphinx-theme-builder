import inspect
import sys
from typing import Any, Dict, List, Optional, Protocol, TextIO, Type

import rich
from rich.text import Text

from ..errors import DiagnosticError

try:
    import build  # noqa
    import click
    import sphinx_autobuild  # type: ignore  # noqa
except ImportError as import_error:
    rich.print(
        DiagnosticError(
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
        ),
        file=sys.stderr,
    )
    sys.exit(1)


class Command(Protocol):
    context_settings: Dict[str, Any]
    interface: List[click.Parameter]

    def run(self, **kwargs: Dict[str, Any]) -> int:
        ...


def create_click_command(cls: Type[Command]) -> click.Command:
    # Use the class docstring as the help string
    help_string = inspect.cleandoc(cls.__doc__)
    # Infer the name, from the known context.
    name = cls.__name__[: -len("Command")].lower()

    # Double check that things are named correctly.
    assert name.capitalize() + "Command" == cls.__name__
    assert name == cls.__module__.split(".")[-1]

    context_settings: Optional[Dict[str, Any]] = None
    if hasattr(cls, "context_settings"):
        context_settings = cls.context_settings

    command = click.Command(
        name=name,
        context_settings=context_settings,
        help=help_string,
        params=cls.interface,
        callback=lambda **kwargs: cls().run(**kwargs),
    )
    return command


def compose_command_line() -> click.Group:
    from .compile import CompileCommand
    from .new import NewCommand
    from .npm import NpmCommand
    from .package import PackageCommand
    from .serve import ServeCommand

    command_classes: List[Type[Command]] = [
        CompileCommand,  # type: ignore
        NewCommand,  # type: ignore
        PackageCommand,  # type: ignore
        ServeCommand,  # type: ignore
        NpmCommand,  # type: ignore
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


def present_click_usage_error(error: click.UsageError, *, stream: TextIO) -> None:
    assert error.ctx

    rich.print(
        Text.from_markup("[red]error:[/] ") + Text(error.format_message()),
        file=stream,
    )

    # Usage
    usage_parts = error.ctx.command.collect_usage_pieces(error.ctx)
    usage = " ".join([error.ctx.command_path] + usage_parts)
    print(file=stream)
    print("Usage:", file=stream)
    print(" ", usage, file=stream)

    # --help
    option = "--help"
    command = error.ctx.command_path
    print(file=stream)
    rich.print(
        f"Try [green]{command} {option}[/] for more information.",
        file=stream,
    )


def main(args: Optional[List[str]] = None) -> None:
    """The entrypoint for command line stuff."""
    cli = compose_command_line()
    try:
        cli(args=args, standalone_mode=False)
    except click.Abort:
        rich.print(r"[cyan]\[stb][/] [red]Aborting![/]", file=sys.stderr)
        sys.exit(1)
    except click.UsageError as error:
        present_click_usage_error(error, stream=sys.stderr)
        sys.exit(error.exit_code)  # uses exit codes 1 and 2
    except click.ClickException as error:
        error.show(sys.stderr)
        sys.exit(error.exit_code)  # uses exit codes 1 and 2
    except DiagnosticError as error:
        rich.print(error, file=sys.stderr)
        sys.exit(3)
    except Exception:
        console = rich.console.Console(stderr=True)
        console.print_exception(
            width=console.width, show_locals=True, word_wrap=True, suppress=[click]
        )
        console.print(
            DiagnosticError(
                reference="crash",
                message="A fatal error occurred.",
                context="See above for a detailed Python traceback.",
                note_stmt=(
                    "If you file an issue, please include the full traceback above."
                ),
                hint_stmt=(
                    "This might be due to an issue in sphinx-theme-builder, one of the "
                    "tools it uses internally, or your code."
                ),
            ),
        )
        sys.exit(4)
