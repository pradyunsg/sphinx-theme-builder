# `stb serve`

Serve the provided documentation path, with livereload on changes.

## Usage

This start a long-running server with live-reload that watches for changes in
the theme or documentation sources (using {pypi}`sphinx-autobuild`).

When a change is made, it will rebuild the assets of the theme, rebuild the
documentation using Sphinx and reload any open browser tabs that are viewing an
HTML page served by the server.

## Options

### `--builder`

The Sphinx builder to build the documentation with.

Allowed values: `html` (default), `dirhtml`

### `--port`

The port to start the server on. Uses a random free port by default.

Allowed values: INTEGER

### `--open-browser / --no-open-browser`

Open the browser after starting live-reload server. This is done by default.

### `--override-theme / --no-override-theme`

Override the `html_theme` value set in `conf.py`. This is not done by default.
