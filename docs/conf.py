# Configuration file for the Sphinx documentation builder.
#
# Full list of options can be found in the Sphinx documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

#
# -- Project information -----------------------------------------------------
#

project = "sphinx-theme-builder"
copyright = "2021, Pradyun Gedam"
author = "Pradyun Gedam"

#
# -- General configuration ---------------------------------------------------
#

extensions = [
    # Sphinx's own extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    # External stuff
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
]
templates_path = ["_templates"]

#
# -- Options for extlinks ----------------------------------------------------
#
extlinks = {
    "pypi": ("https://pypi.org/project/%s/", "%s"),
}

#
# -- Options for intersphinx -------------------------------------------------
#
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}

#
# -- Options for TODOs -------------------------------------------------------
#
todo_include_todos = True

#
# -- Options for Markdown files ----------------------------------------------
#
myst_enable_extensions = [
    "deflist",
]
myst_heading_anchors = 3

#
# -- Options for HTML output -------------------------------------------------
#

html_theme = "furo"
html_title = "Sphinx Theme Builder"
