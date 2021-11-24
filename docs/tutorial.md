# Getting Started

Follow this tutorial, to get a basic understanding of the workflow of developing a Sphinx theme with this tool.

This tutorial expects that the reader has working knowledge of:

- Terminal / Command Prompt
- Python virtual environments
- Web technologies (HTML/JS/CSS)

[sphinx]: https://www.sphinx-doc.org/en/master/
[jinja]: https://palletsprojects.com/p/jinja/

## Installation

As a first step, let's install this tool with the `cli` extra, in a clean virtual environment:

```shell
$ pip install "sphinx-theme-builder[cli]"
```

## Create a new theme

To create a new theme, you can use the `stb new` command.

```shell
$ stb new my-awesome-sphinx-theme
```

You will be prompted to answer a few questions. Once they've been answered, this command will generate a scaffold for your theme in a folder named `my-awesome-sphinx-theme`.

For the rest of this tutorial, we're going to exclusively work in this directory, so it's sensible to `cd` into it.

```shell
$ cd my-awesome-sphinx-theme
```

[cookiecutter]: https://cookiecutter.readthedocs.io/
[cruft]: https://github.com/cruft/cruft

## Install the theme

To work with your theme, it is necessary to install it in the virtual environment. Let's do an editable install, since that's usually what you would want to do for development.

```shell
$ pip install -e .
```

## Start the development server

To start a development server, you use the `stb serve` command. It needs a path to a directory containing Sphinx documentation, so we'll use the demo documentation that comes as part of the default scaffold:

```shell
$ stb serve docs/
```

This command will do a few things (we'll get to details of this later) and, after a short delay, opens your default browser to view the built documentation. Keep this terminal open/running.

The development server simplifies the workflow for seeing how a change affects the generated documentation fairly straightforward -- save changes to a file, switch to the browser and the browser will update to reflect those changes.

## Making changes

To try out how the development server handles changes, create a new `sections/article.html` file in the `src/{your_package_name}/theme/{your_theme_name}` with the following content:

```jinja
{{ content }}
```

The server should do a few things and the page will automagically reload with the new page contents.

### How it works

The development server listens for changes in your theme or the documentation (i.e. when a file is saved/renamed/moved). When it detects that a change has been made, the server will:

1. Recompile your theme's assets
2. Rebuild the Sphinx documentation it is serving
3. Automagically reload open browser tabs of HTML pages served by it

If the theme's asset compilation or the documentation build (with Sphinx) fails, the server will print something in the terminal window about the failure.

## Stopping the server

To stop the server, focus on the terminal where the server is running and press {kbd}`Ctrl`+{kbd}`C`.

## Packaging the theme

When you wish to publish your theme on PyPI, you will need to package your theme into a few distribution files and upload these files to PyPI. This makes it possible to install the package for your theme, which can be downloaded and installed with `pip`.

To generate the distribution files, run:

```shell
$ stb package
```

This will generate files in `dist/`, that contain the relevant distribution files for your project. These can be uploaded to PyPI using {pypi}`twine`.

## Next Steps

Go write a Sphinx theme!
