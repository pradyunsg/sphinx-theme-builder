"""User Interface helpers."""

from typing import Any

import rich


def log(*objects: Any) -> None:
    rich.print(r"[cyan]\[stb][/]", *objects)
