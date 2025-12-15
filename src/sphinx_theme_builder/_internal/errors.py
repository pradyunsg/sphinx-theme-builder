"""Exceptions raised from within this package."""

from diagnostic import DiagnosticError


class STBError(DiagnosticError):
    docs_index = "https://sphinx-theme-builder.rtfd.io/errors/#{code}"
