"""Exceptions raised from within this package."""

import re
from typing import TYPE_CHECKING, Optional, Union

from rich.console import Console, ConsoleOptions, RenderResult
from rich.text import Text

if TYPE_CHECKING:
    from typing import Literal

_DOCS_URL = "https://sphinx-theme-builder.rtfd.io/errors/#{}"


def _is_kebab_case(s: str) -> bool:
    return re.match(r"^[a-z]+(-[a-z]+)*$", s) is not None


def _prefix_with_indent(
    s: Union[Text, str],
    console: Console,
    *,
    width_offset: int = 0,
    prefix: str,
    indent: str,
) -> Text:
    if isinstance(s, Text):
        text = s
    else:
        text = console.render_str(s)

    lines = text.wrap(console, console.width - width_offset)

    return console.render_str(prefix) + console.render_str(f"\n{indent}").join(lines)


class DiagnosticError(Exception):
    reference: str

    def __init__(
        self,
        *,
        kind: 'Literal["error", "warning"]' = "error",
        reference: Optional[str] = None,
        message: Union[str, Text],
        context: Optional[Union[str, Text]],
        hint_stmt: Optional[Union[str, Text]],
        note_stmt: Optional[Union[str, Text]] = None,
    ) -> None:
        # Ensure a proper reference is provided.
        if reference is None:
            assert hasattr(self, "reference"), "error reference not provided!"
            reference = self.reference
        assert _is_kebab_case(reference), "error reference must be kebab-case!"

        self.kind = kind
        self.reference = reference

        self.message = message
        self.context = context

        self.note_stmt = note_stmt
        self.hint_stmt = hint_stmt

        super().__init__(
            f"<{self.__class__.__name__}: {_DOCS_URL.format(self.reference)}>"
        )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"reference={self.reference!r}, "
            f"message={self.message!r}, "
            f"context={self.context!r}, "
            f"note_stmt={self.note_stmt!r}, "
            f"hint_stmt={self.hint_stmt!r}"
            ")>"
        )

    def __rich_console__(
        self,
        console: Console,
        options: ConsoleOptions,
    ) -> RenderResult:
        colour = "red" if self.kind == "error" else "yellow"

        yield f"[{colour} bold]{self.kind}[/]: [bold]{self.reference}[/]"

        # Present the main message, with relevant context indented.
        if not options.ascii_only:
            yield ""
            if self.context is not None:
                yield _prefix_with_indent(
                    self.message,
                    console,
                    width_offset=2,
                    prefix=f"[{colour}]×[/] ",
                    indent=f"[{colour}]│[/] ",
                )
                yield _prefix_with_indent(
                    self.context,
                    console,
                    width_offset=4,
                    prefix=f"[{colour}]╰─>[/] ",
                    indent=f"[{colour}]   [/] ",
                )
            else:
                yield _prefix_with_indent(
                    self.message,
                    console,
                    width_offset=4,
                    prefix="[red]×[/] ",
                    indent="  ",
                )
        else:  # coverage: skip
            yield console.render_str(f"[{colour}]x[/] ") + self.message
            if self.context is not None:
                yield ""
                yield self.context

        if self.note_stmt is not None or self.hint_stmt is not None:
            yield ""

        if self.note_stmt is not None:
            yield _prefix_with_indent(
                self.note_stmt,
                console,
                width_offset=6,
                prefix="[magenta bold]note[/]: ",
                indent="      ",
            )
        if self.hint_stmt is not None:
            yield _prefix_with_indent(
                self.hint_stmt,
                console,
                width_offset=6,
                prefix="[cyan bold]hint[/]: ",
                indent="      ",
            )

        yield ""
        yield f"Link: {_DOCS_URL.format(self.reference)}"


if __name__ == "__main__":
    import rich

    errors = [
        DiagnosticError(
            reference="ooops-an-error-occured",
            message=(
                "This is an error message describing the issues."
                "\nIt can have multiple lines."
            ),
            context=None,
            hint_stmt=None,
        ),
        DiagnosticError(
            reference="ooops-an-error-occured",
            message=(
                "This is an error message describing the issues."
                "\nIt can have multiple lines."
            ),
            context=(
                "This is some context associated with that error."
                "\nAny relevant additional details are mentioned here."
            ),
            hint_stmt=(
                "This is a hint, that will help you figure this out."
                "\nAnd the hint can have multiple lines."
            ),
            note_stmt=(
                "This is to draw your attention toward about something important."
                "\nAnd this can also have multiple lines."
            ),
        ),
        DiagnosticError(
            reference="you-have-been-warned",
            kind="warning",
            message=(
                "This is an warning message describing the issues."
                "\nIt can have multiple lines."
            ),
            context=(
                "This is some context associated with that warning."
                "\nAny relevant additional details are mentioned here."
            ),
            hint_stmt=(
                "This is a hint, that will help you figure this out."
                "\nAnd the hint can have multiple lines."
            ),
            note_stmt=(
                "This is to draw your attention toward about something important."
                "\nAnd this can also have multiple lines."
            ),
        ),
    ]

    for error in errors:
        rich.get_console().rule()
        rich.print(error)
    rich.get_console().rule()
