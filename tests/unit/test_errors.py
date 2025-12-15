"""Test the presentation style of exceptions."""

import textwrap
from io import StringIO
from typing import TYPE_CHECKING

import pytest
import rich
import rich.console
import rich.text

from sphinx_theme_builder._internal.errors import DiagnosticError

if TYPE_CHECKING:
    from typing import Literal


class TestDiagnosticErrorInitialisation:
    def test_fails_without_reference(self) -> None:
        class DerivedError(DiagnosticError):
            pass

        with pytest.raises(AssertionError) as exc_info:
            DerivedError(message="", context=None, hint_stmt=None)

        assert str(exc_info.value) == "error reference not provided!"

    def test_can_fetch_reference_from_subclass(self) -> None:
        class DerivedError(DiagnosticError):
            reference = "subclass-reference"

        obj = DerivedError(message="", context=None, hint_stmt=None)
        assert obj.reference == "subclass-reference"

    def test_can_fetch_reference_from_arguments(self) -> None:
        class DerivedError(DiagnosticError):
            pass

        obj = DerivedError(
            message="", context=None, hint_stmt=None, reference="subclass-reference"
        )
        assert obj.reference == "subclass-reference"

    @pytest.mark.parametrize(
        "name",
        [
            "BADNAME",
            "BadName",
            "bad_name",
            "BAD_NAME",
            "_bad",
            "bad-name-",
            "bad--name",
            "-bad-name",
            "bad-name-due-to-1-number",
        ],
    )
    def test_rejects_non_kebab_case_names(self, name: str) -> None:
        class DerivedError(DiagnosticError):
            reference = name

        with pytest.raises(AssertionError) as exc_info:
            DerivedError(message="", context=None, hint_stmt=None)

        assert str(exc_info.value) == "error reference must be kebab-case!"


def assert_presentation_matches(
    error: DiagnosticError,
    expected: str,
    *,
    color_system: 'Literal["auto", "standard", "256", "truecolor", "windows"] | None',
) -> None:
    expected_output = textwrap.dedent(expected)

    stream = StringIO()
    console = rich.console.Console(file=stream, color_system=color_system)
    console.print(error)

    assert stream.getvalue() == expected_output


class TestDiagnosticPipErrorPresentation:
    def test_complete_string(self) -> None:
        # GIVEN
        error = DiagnosticError(
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
                "This is to draw your [b]attention[/] toward about something important."
                "\nAnd this can also have multiple lines."
            ),
        )

        # WHEN / THEN
        assert str(error) == (
            "<DiagnosticError: "
            "https://sphinx-theme-builder.rtfd.io/errors/#ooops-an-error-occured"
            ">"
        )
        assert repr(error) == (
            "<DiagnosticError("
            "reference='ooops-an-error-occured', "
            "message='This is an error message describing the issues.\\n"
            "It can have multiple lines.', "
            "context='This is some context associated with that error.\\n"
            "Any relevant additional details are mentioned here.', "
            "note_stmt='This is to draw your [b]attention[/] toward about something important.\\n"
            "And this can also have multiple lines.', "
            "hint_stmt='This is a hint, that will help you figure this out.\\n"
            "And the hint can have multiple lines.'"
            ")>"
        )

    def test_complete(self) -> None:
        assert_presentation_matches(
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
                    "This is to draw your [b]attention[/] toward about something important."
                    "\nAnd this can also have multiple lines."
                ),
            ),
            """\
                error: ooops-an-error-occured

                × This is an error message describing the issues.
                │ It can have multiple lines.
                ╰─> This is some context associated with that error.
                    Any relevant additional details are mentioned here.

                note: This is to draw your attention toward about something important.
                      And this can also have multiple lines.
                hint: This is a hint, that will help you figure this out.
                      And the hint can have multiple lines.
                link: https://sphinx-theme-builder.rtfd.io/errors/#ooops-an-error-occured
            """,
            color_system=None,
        )

    def test_complete_colors(self) -> None:
        assert_presentation_matches(
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
                hint_stmt=rich.text.Text(
                    "This is a hint, that will help you figure this out."
                    "\nAnd the [b]hint[/] can have multiple lines."
                ),
                note_stmt=(
                    "This is to draw your [b]attention[/] toward about something important."
                    "\nAnd this can also have multiple lines."
                ),
            ),
            # Yes, I know this is dumb.
            """\
                \x1b[1;31merror\x1b[0m: \x1b[1mooops-an-error-occured\x1b[0m

                \x1b[31m×\x1b[0m This is an error message describing the issues.
                \x1b[31m│\x1b[0m It can have multiple lines.
                \x1b[31m╰─>\x1b[0m This is some context associated with that error.
                \x1b[31m   \x1b[0m Any relevant additional details are mentioned here.

                \x1b[1;35mnote\x1b[0m: This is to draw your \x1b[1mattention\x1b[0m toward about something important.
                      And this can also have multiple lines.
                \x1b[1;36mhint\x1b[0m: This is a hint, that will help you figure this out.
                      And the [b]hint[/] can have multiple lines.
                \x1b[1mlink\x1b[0m: \x1b[4;94mhttps://sphinx-theme-builder.rtfd.io/errors/#ooops-an-error-occured\x1b[0m
            """,
            color_system="256",
        )

    def test_no_note_no_hint_no_context(self) -> None:
        # GIVEN
        assert_presentation_matches(
            DiagnosticError(
                reference="ooops-an-error-occured",
                message=(
                    "This is an error message describing the issues."
                    "\nIt can have multiple lines."
                ),
                context=None,
                hint_stmt=None,
            ),
            """\
                error: ooops-an-error-occured

                × This is an error message describing the issues.
                  It can have multiple lines.

                link: https://sphinx-theme-builder.rtfd.io/errors/#ooops-an-error-occured
            """,
            color_system=None,
        )

    def test_no_note_no_hint(self) -> None:
        # GIVEN
        assert_presentation_matches(
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
                hint_stmt=None,
            ),
            """\
                error: ooops-an-error-occured

                × This is an error message describing the issues.
                │ It can have multiple lines.
                ╰─> This is some context associated with that error.
                    Any relevant additional details are mentioned here.

                link: https://sphinx-theme-builder.rtfd.io/errors/#ooops-an-error-occured
            """,
            color_system=None,
        )

    def test_no_note(self) -> None:
        # GIVEN
        assert_presentation_matches(
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
            ),
            """\
                error: ooops-an-error-occured

                × This is an error message describing the issues.
                │ It can have multiple lines.
                ╰─> This is some context associated with that error.
                    Any relevant additional details are mentioned here.

                hint: This is a hint, that will help you figure this out.
                      And the hint can have multiple lines.
                link: https://sphinx-theme-builder.rtfd.io/errors/#ooops-an-error-occured
            """,
            color_system=None,
        )

    def test_no_hint(self) -> None:
        # GIVEN
        assert_presentation_matches(
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
                hint_stmt=None,
                note_stmt=(
                    "This is to draw your [b]attention[/] toward about something important."
                    "\nAnd this can also have multiple lines."
                ),
            ),
            """\
                error: ooops-an-error-occured

                × This is an error message describing the issues.
                │ It can have multiple lines.
                ╰─> This is some context associated with that error.
                    Any relevant additional details are mentioned here.

                note: This is to draw your attention toward about something important.
                      And this can also have multiple lines.
                link: https://sphinx-theme-builder.rtfd.io/errors/#ooops-an-error-occured
            """,
            color_system=None,
        )
