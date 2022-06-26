# Error Index

Inspired by the [Rust Compiler Error Index], this page describes the various
errors that may be presented by `sphinx-theme-builder`, indicating known causes
as well as potential solutions.

[rust compiler error index]: https://doc.rust-lang.org/error-index.html

## crash

This error suggests that there is an unexpected exception raised within
`sphinx-theme-builder`. This is usually a symptom of an incorrect
assumption/expectation or a bug in the implementation of `sphinx-theme-builder`.

This error will print a detailed traceback above it. It is recommended to report
this issue as a crash report, on the [issue tracker].

[issue tracker]: https://github.com/pradyunsg/sphinx-theme-builder/issues

## nodeenv-creation-failed

This error indicates that a NodeJS environment (nodeenv) could not be created,
for some reason. Typically, the reason for the failure is indicated by the
output above the error.

A `urllib.error.HTTPError` indicates that the issue is related to the network or
the availability of NodeJS release files. It may mean the node version that this
tool is trying to fetch is no longer available, for example if there is no
compatible NodeJS binary for the operating system.

When this error is encountered, a good place to look at is the {pypi}`nodeenv`
project's documentation and issue tracker.

## unknown-value-for-STB_USE_SYSTEM_NODE

This error is raised when the user sets the `STB_USE_SYSTEM_NODE` environment
variable to an unsupported value.

The environment variable only supports truthy-values (`true` and `1`,
case-insensitive) and any other value will cause this error to be raised.

## can-not-use-system-node-on-windows

This error is raised when the user tries to use the system NodeJS installation
on Windows.

The underlying tooling that Sphinx Theme Builder uses ({pypi}`nodeenv`) does not
support using an existing system NodeJS installation for creating the nodeenv,
so this is not permitted.

Windows users should unset the `STB_USE_SYSTEM_NODE` environment variable in
such cases.

## js-build-failed

This error indicates that the build step using the Javascript tooling failed,
which is a theme-specific issue.

Sphinx Theme Builder executes `npm run-script build` for running the Javascript
tooling. When that fails, this error is raised which means that something went
wrong in the Javascript build pipeline of the theme that is being
built/packaged.

Typically, there is a JS error reported immediately above this error coming from
the theme-specific tooling. For more details on the failure, that error is what
needs to be looked at (and possibly, put into a search engine).

## js-install-failed

This error indicates that the install step for the Javascript tooling failed,
which is a theme-specific issue.

Sphinx Theme Builder executes `npm install` for installing the Javascript
tooling that the theme declares a dependency on. When that fails, this error is
raised which means that something went wrong in the installation of the JS
dependencies of the theme that is being built/packaged.

Typically, there is a JS error reported immediately above this error coming from
the theme-specific tooling. For more details on the failure, that error is what
needs to be looked at (and possibly, put into a search engine).

## nodeenv-unhealthy-npm-not-found

This error indicates that the nodeenv created for building this theme is broken,
and does not have an `npm` executable. Typically, this is a symptom of an
incomplete cleanup and the resolution is to delete the `.nodeenv` directory.

If this happens while performing parallel builds (which is not supported at this
time), this can be caused by a race condition due to the lack of support for
this mode of usage.

## nodeenv-unhealthy-file-not-found

This error indicates that the nodeenv created for building this theme is broken,
and does not contain a file that should have been there (the `node` executable).
Typically, this is a symptom of an incomplete cleanup and the resolution is to
delete the `.nodeenv` directory.

If this happens while performing parallel builds (which is not supported at this
time), this can be caused by a race condition due to the lack of support for
this mode of usage.

## nodeenv-unhealthy-subprocess-failure

This error indicates that the nodeenv created for building this theme is broken,
and can not be used.

Sphinx Theme Builder executes `node --version` using the NodeJS available in the
nodeenv to determine what version is available in the nodeenv. This error
indicates that this subprocess failed, which should never happen for a valid and
functional nodeenv.

This is not a typical failure and may be a symptom of a different underlying
issue (incompatible architecture, broken OS libraries etc). It may be possible
to work around this by deleting the `.nodeenv` directory and trying again.

## nodeenv-version-mismatch

This error indicates that the nodeenv created for building this theme does not
match the declared requirements of the theme, and can not be used.

Typically, this is because the declared requirement of the theme has been
changed. If that's the case, then deleting the `.nodeenv` directory and trying
again will usually resolve this issue.

If the build is being attempted with `STB_USE_SYSTEM_NODE=true`, this error
reflects that the system NodeJS version that does not match the theme
requirements.

## unable-to-cleanup-node-modules

This error indicates that the `node_modules` folder could not be deleted. It is
not a typical error and will need diagnosis of why the deletion might have
failed (eg: permission issues, filesystem issues).

## invalid-pyproject-toml

This error indicates that the theme does not have a valid `pyproject.toml` file
in the root, due to the contents of the file. Typically, this is related to the
`build-system` table or the `project` table and mentions the problematic key.

## pyproject-missing

This error indicates that theme does not have a `pyproject.toml` file in the
root directory of the theme's package (typically, the repository root). It is
required for using Sphinx Theme Builder.

## pyproject-could-not-parse

This error indicates that the theme do not have a valid `pyproject.toml` file.
It needs to be a valid TOML 1.0.0 file.

## pyproject-no-project-table

This error indicates that the `pyproject.toml` file in the theme does not
contain the `[project]` table. That table provides required metadata and must be
specified.

## pyproject-no-name-in-project-table

This error indicates that the `pyproject.toml` file in the theme does not
contain the required `name` key in the `[project]` table.

## pyproject-non-canonical-name

This error indicates that the `pyproject.toml` file in the theme has a `name`
key that is not formatted in a canonical format. This needs to be a
`dashed-name-with-only-lowercase-characters`.

## pyproject-invalid-version

This error indicates that the `pyproject.toml` file in the theme has a `version`
key that is not a string.

## project-init-missing

This error indicates that the theme's `__init__.py` file could not be found.

## project-init-invalid-syntax

This error indicates that the theme's `__init__.py` file is not a valid Python
file. This file is parsed by Sphinx Theme Builder, to look up the Python version
of that file.

## project-double-version-declaration

This error indicates that the theme has declared its version in both
`__init__.py` file and the `pyproject.toml` file. This is not supported.

## project-missing-dynamic-version

This error indicates that the theme's `__init__.py` file does not contain a
version declaration in the form expected by Sphinx Theme Builder.

This needs to be a top-level assignment of the form `__version__ = <string>`.

## project-improper-dynamic-version

This error indicates that the `pyproject.toml` file in the theme has a `version`
key _and_ declares that the version will be picked up from the `__init__.py`
file (by including version in the `dynamic` key).

## project-no-version-declaration

This error indicates that Sphinx Theme Builder could not locate a version
declaration for this theme. Typically, this is because the version has not been
declared in either of the `pyproject.toml` or `__init__.py` files.

## project-invalid-version

This error indicates that the theme's declared version is not a valid Python
Package version (see {pep}`440` for the specification).

## no-license-declared

This error indicates that the `pyproject.toml` file does not declare a license,
which is not permitted when using Sphinx Theme Builder.

## unsupported-dynamic-keys

This error indicates that there are unsupported values the `dynamic` key in
`pyproject.toml` file.

## no-node-version

This error indicates that no NodeJS version was configured in the
`pyproject.toml` file.

## missing-theme-conf

This error indicates that the `theme.conf` file for the theme could not be
located.

This is typically a a genuinely missing file, a symptom of a misconfiguration or
incorrect filesystem layout of the package. The misconfiguration is typically
forgetting to set `theme-name` in `[tool.sphinx-theme-builder]` in
pyproject.toml, when it does not match the PyPI package name.

## missing-javascript

This error indicates that the Javascript file for the theme could not be
located.

This is typically a a genuinely missing file, a symptom of a misconfiguration or
incorrect filesystem layout of the package. The misconfiguration is typically
forgetting to set `theme-name` in `[tool.sphinx-theme-builder]` in
pyproject.toml, when it does not match the PyPI package name.

## missing-stylesheet

This error indicates that the CSS file for the theme could not be located.

This is typically a a genuinely missing file, a symptom of a misconfiguration or
incorrect filesystem layout of the package. The misconfiguration is typically
forgetting to set `theme-name` in `[tool.sphinx-theme-builder]` in
pyproject.toml, when it does not match the PyPI package name.

## could-not-read-theme-conf

This error indicates that `theme.conf` could not be read.

Sphinx Theme Builder tries to read the `theme.conf` file of the theme being
built, parse it and read certain configuration variables declared in it. This
error is presented when that operation fails. More details are typically
available from the "context" information provided in the error message (the line
after "Could not open/parse).

If the file is missing, it should be created, as described in
[Sphinx's theme creation documentation](https://www.sphinx-doc.org/en/master/development/theming.html#creating-themes).

## theme-conf-incorrect-stylesheet

This error indicates that the style file declared in `theme.conf` does not match
the stylesheet that was expected based on the theme name.

Sphinx Theme Builder enforces this consistency to make it easier to avoid
collisions within derived themes and ensure that CSS file for the theme could
not be located.

## missing-command-line-dependencies

This error indicates that one or more of the dependencies that are needed to use
the `stb` command are not installed.

This is typically a symptom of doing `pip install sphinx-theme-builder` instead
of `pip install "sphinx-theme-builder[cli]"`.

## can-not-overwrite-existing-python-project

This error is raised to prevent users from overwriting existing Python projects
with `stb new`, since that command does not attempt to preserve any file and is
not designed to be used on an existing Python project.

## cookiecutter-failed

This error indicates that `stb new` could not create the repository. This is
currently expected as the repository that `stb new` tries to use is not set up.

## no-nodeenv

This error is raised by `stb npm` when the user tries to use it without creating
the nodeenv for the project. Typically, it is expected that users will run
`stb compile` once before trying to run `stb npm`.

## autobuild-failed

This error is raised when `sphinx-autobuild` exits with an error, which is
typically caused by interrupting a fatal error (or interrupt). The information
about the underlying issue is typically available in the output of
`sphinx-autobuild` and is available above this error.
