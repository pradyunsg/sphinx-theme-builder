# Error Index

Inspired by the [Rust Compiler Error Index], this page describes the various
errors that may be presented by `sphinx-theme-builder`, indicating known causes
as well as potential solutions.

<!--
  Editor's note: Ensure that each error has a "What you can do" part to it.
-->

[rust compiler error index]: https://doc.rust-lang.org/error-index.html

## crash

There is an unexpected exception raised within `sphinx-theme-builder`. This is
usually a symptom of an incorrect assumption/expectation or a bug in the
implementation of `sphinx-theme-builder`.

**What you can do:** It is recommended to report this issue as a crash report,
on the [issue tracker]. This error will print a detailed traceback above it,
which should be included.

[issue tracker]: https://github.com/pradyunsg/sphinx-theme-builder/issues

## nodeenv-creation-failed

A NodeJS environment (nodeenv) could not be created, for some reason. Typically,
the reason for the failure is indicated by the output above the error. This is
an error from the underlying tooling that `sphinx-theme-builder` uses.

A `urllib.error.HTTPError` indicates that the issue is related to the network or
the availability of NodeJS release files. It may mean the node version that this
tool is trying to fetch is no longer available, for example if there is no
compatible NodeJS binary for the operating system.

**What you can do:** When this error is encountered, a good place to look at is
the {pypi}`nodeenv` project's documentation and issue tracker.

## non-boolean-env-variable-value

This error is raised when the user sets the a boolean environment variable to an
invalid value. The valid values for boolean environment variables are `true`,
`false`, `1` and `0`. They are case-insensitive. Providing any other value will
cause this error to be raised.

**What you can do:** Provide a valid value, for the environment variable
involved.

## can-not-use-system-node-on-windows

This error is raised when the user tries to use the system NodeJS installation
on Windows.

The underlying tooling that Sphinx Theme Builder uses ({pypi}`nodeenv`) does not
support using an existing system NodeJS installation for creating the nodeenv,
so this is not permitted.

**What you can do:** Unset the `STB_USE_SYSTEM_NODE` environment variable, since
it is not possible to use the system NodeJS installation on Windows.

## js-build-failed

This error indicates that the build step using the Javascript tooling failed,
which is a theme-specific issue. Typically, there is a JS error reported by the
theme-specific tooling immediately above this error.

Sphinx Theme Builder executes `npm run-script build` for running the Javascript
tooling. When that fails, this error is raised which means that something went
wrong in the Javascript build pipeline of the theme that is being
built/packaged.

**What you can do:** Look into the JS error reported, since that error is what
needs to be looked at (and possibly, put into a search engine).

## js-install-failed

This error indicates that the install step for the Javascript tooling failed,
which is a theme-specific issue. Typically, there is a JS error reported by the
theme-specific tooling immediately above this error.

Sphinx Theme Builder executes `npm install` for installing the Javascript
tooling that the theme declares a dependency on. When that fails, this error is
raised which means that something went wrong in the installation of the JS
dependencies of the theme that is being built/packaged.

**What you can do:** Look into the JS error reported, since that error is what
needs to be looked at (and possibly, put into a search engine).

## nodeenv-unhealthy-npm-not-found

This error indicates that the nodeenv created for building this theme is broken,
and does not have an `npm` executable. Typically, this is a symptom of an
incomplete cleanup.

**What you can do:** Deleting the `.nodeenv` directory and trying again will
usually resolve this issue.

If this happens while performing multiple builds of the same theme in parallel
(which is not supported at this time), this is likely caused by a race condition
due to the lack of support for this mode of usage. You'll need to ensure that no
parallel builds are occurring in the same directory.

## nodeenv-unhealthy-file-not-found

This error indicates that the nodeenv created for building this theme is broken,
and does not contain a file that should have been there (the `node` executable).
Typically, this is a symptom of an incomplete cleanup.

**What you can do:** Deleting the `.nodeenv` directory and trying again will
usually resolve this issue.

If this happens while performing multiple builds of the same theme in parallel
(which is not supported at this time), this is likely caused by a race condition
due to the lack of support for this mode of usage. You'll need to ensure that no
parallel builds are occurring in the same directory.

## nodeenv-unhealthy-subprocess-failure

This error indicates that the nodeenv created for building this theme is broken,
and can not be used.

Sphinx Theme Builder executes `node --version` using the NodeJS available in the
nodeenv to determine what version is available in the nodeenv. This error
indicates that this subprocess failed, which should never happen for a valid and
functional nodeenv.

**What you can do:** This is not a typical failure and may be a symptom of a
different underlying issue (incompatible architecture, broken OS libraries etc).
It may be possible to work around this by deleting the `.nodeenv` directory and
trying again.

## nodeenv-version-mismatch

This error indicates that the nodeenv created for building this theme does not
match the declared requirements of the theme, and can not be used. Typically,
this is because the declared requirement of the theme has been changed.

**What you can do:** Deleting the `.nodeenv` directory and trying again will
usually resolve this issue. If it does not, please see
{ref}`controlling-nodejs`. If you're a redistributor of software (rather than a
user or theme author), the aforementioned link should provide relevant
information.

## unable-to-cleanup-node-modules

This error indicates that the `node_modules` folder could not be deleted.

**What you can do:** This is not a typical failure and will need diagnosis of
why the deletion might have failed (eg: permission issues, filesystem issues).

## invalid-pyproject-toml

This error indicates that the theme does not have a valid `pyproject.toml` file
in the root, due to the contents of the file. Typically, this is related to the
the `project` table and mentions the problematic key.

**What you can do:** Resolve the issue as suggested by the error message. You
can find more details by looking up documentation about the `[project]` table
(eg: {pep}`621`).

## invalid-import-names

This error indicates that the `import-names` declared in the `pyproject.toml`
file do not match the expected value, which is derived from the project's name.

**What you can do:** Remove the `import-names` key in the `[project]` table of
the `pyproject.toml` file, or update it to match the expected value from the
error message.

## pyproject-missing

This error indicates that theme does not have a `pyproject.toml` file in the
root directory of the theme's package (typically, the repository root). It is
required for using Sphinx Theme Builder.

**What you can do:** Create a `pyproject.toml` file and try again. You'll get a
new error, which will help guide you forward.

## pyproject-could-not-parse

This error indicates that the theme do not have a valid `pyproject.toml` file.
It needs to be a valid TOML 1.0.0 file.

**What you can do:** Investigate why the file is not a valid TOML file and fix
the issue.

## pyproject-no-project-table

This error indicates that the `pyproject.toml` file in the theme does not
contain the `[project]` table. That table provides required metadata and must be
specified.

**What you can do:** Declare your project's metadata in the `[project]` table.
See {pep}`621` for more details on the syntax.

## pyproject-no-name-in-project-table

This error indicates that the `pyproject.toml` file in the theme does not
contain the required `name` key in the `[project]` table.

**What you can do:** Declare your project's name in the `[project]` table.

## pyproject-non-canonical-name

This error indicates that the `pyproject.toml` file in the theme has a `name`
key that is not formatted in a canonical format. This needs to be a
`dashed-name-with-only-lowercase-characters`.

**What you can do:** Fix your project's `name` in the `[project]` table.

## pyproject-invalid-version

This error indicates that the `pyproject.toml` file in the theme has a `version`
key that is not a string.

**What you can do:** Fix your project's `version` in the `[project]` table.

## project-init-missing

This error indicates that the theme's `__init__.py` file could not be found.

**What you can do:** Move/create your theme's importable package in the location
expected. See {doc}`filesystem-layout` for more details.

## project-init-invalid-syntax

This error indicates that the theme's `__init__.py` file is not a valid Python
file. This file is parsed by Sphinx Theme Builder, to look up the Python version
of that file.

**What you can do:** Fix the file to be valid Python code.

## project-double-version-declaration

This error indicates that the theme has declared its version in both
`__init__.py` file and the `pyproject.toml` file. This is not supported.

**What you can do:** Declare your theme's version in only one location.
Typically, you can do this by removing the version declaration in the
`pyproject.toml` file.

## project-missing-dynamic-version

This error indicates that the theme's `__init__.py` file does not contain a
version declaration in the form expected by Sphinx Theme Builder.

This needs to be a top-level assignment of the form `__version__ = <string>`.

**What you can do:** Declare your theme's version in the form expected.

## project-improper-dynamic-version

This error indicates that the `pyproject.toml` file in the theme has a `version`
key _and_ declares that the version will be picked up from the `__init__.py`
file (by including version in the `dynamic` key).

**What you can do:** Declare your theme's version in the form expected.

## project-no-version-declaration

This error indicates that Sphinx Theme Builder could not locate a version
declaration for this theme. Typically, this is because the version has not been
declared in either of the `pyproject.toml` or `__init__.py` files.

**What you can do:** Declare your theme's version in the `pyproject.toml` file
or in the theme's "base" `__init__.py` file.

## project-invalid-version

This error indicates that the theme's declared version is not a valid Python
Package version (see {pep}`440` for the specification).

**What you can do:** Fix your theme's version.

## no-license-declared

This error indicates that the `pyproject.toml` file does not declare a license,
which is not permitted when using Sphinx Theme Builder.

**What you can do:** Declare a license.

## unsupported-dynamic-keys

This error indicates that there are unsupported values the `dynamic` key in
`pyproject.toml` file.

**What you can do:** Remove the unsupported values.

## no-node-version

This error indicates that no NodeJS version was configured in the
`pyproject.toml` file.

**What you can do:** Configure the NodeJS version in the theme's
`pyproject.toml` file.

## node-version-mismatch

This error indicates that the NodeJS version in the nodeenv does not match what
was configured in the `pyproject.toml` file.

**What you can do:** Typically, this is only seen when
{ref}`the default NodeJS handling is overridden<controlling-nodejs>` and is a
symptom of misconfiguration (either of sphinx-theme-builder or within the
environment). Ensure that a matching NodeJS version for the project being build
is available and, if so, delete the `.nodeenv` directory and try again.

If this happens while performing multiple builds of the same theme in parallel
(which is not supported at this time), this is likely caused by a race condition
due to the lack of support for this mode of usage. You'll need to ensure that no
parallel builds are occurring in the same directory.

## missing-theme-conf

This error indicates that the `theme.conf` file for the theme could not be
located.

This is typically a genuinely missing file, a symptom of a misconfiguration or
incorrect filesystem layout of the package. The misconfiguration is typically
forgetting to set `theme-name` in `[tool.sphinx-theme-builder]` in
pyproject.toml, when it does not match the PyPI package name.

**What you can do:** Ensure that your theme name is correct and, if so,
move/create the `theme.conf` file, in the expected location. If you're creating
this file, you can find more details in
[Sphinx's theme creation documentation](https://www.sphinx-doc.org/en/master/development/theming.html#creating-themes).

## missing-javascript

This error indicates that the Javascript file for the theme could not be
located.

This is typically a genuinely missing file, a symptom of a misconfiguration or
incorrect filesystem layout of the package. The misconfiguration is typically
forgetting to set `theme-name` in `[tool.sphinx-theme-builder]` in
pyproject.toml, when it does not match the PyPI package name.

**What you can do:** Ensure that your theme name is correct and, if so, ensure
that the Javascript file is available, in the expected location.

## missing-stylesheet

This error indicates that the CSS file for the theme could not be located.

This is typically a genuinely missing file, a symptom of a misconfiguration or
incorrect filesystem layout of the package. The misconfiguration is typically
forgetting to set `theme-name` in `[tool.sphinx-theme-builder]` in
pyproject.toml, when it does not match the PyPI package name.

**What you can do:** Ensure that your theme name is correct and, if so, ensure
that the CSS file is available in the expected location.

## could-not-read-theme-conf

This error indicates that `theme.conf` could not be read.

Sphinx Theme Builder tries to read the `theme.conf` file of the theme being
built, parse it and read certain configuration variables declared in it. This
error is presented when that operation fails. More details are typically
available from the "context" information provided in the error message (the line
after "Could not open/parse).

**What you can do:** Ensure that this file can be pasted as an INI file.

## theme-conf-incorrect-stylesheet

This error indicates that the style file declared in `theme.conf` does not match
the stylesheet that was expected based on the theme name.

Sphinx Theme Builder enforces this consistency to make it easier to avoid
collisions within derived themes and ensure that CSS file for the theme could
not be located.

**What you can do:** Update the filename of the CSS file in `theme.conf`, to
match what is expected. You may also need to update your build system to
generate the file in the corresponding location.

## missing-command-line-dependencies

This error indicates that one or more of the dependencies that are needed to use
the `stb` command are not installed.

This is typically a symptom of doing `pip install sphinx-theme-builder` instead
of `pip install "sphinx-theme-builder[cli]"`.

**What you can do:** Run `pip install "sphinx-theme-builder[cli]"` to install
the missing dependencies.

## can-not-overwrite-existing-python-project

This error is raised to prevent users from overwriting existing Python projects
with `stb new`, since that command does not attempt to preserve any file and is
not designed to be used on an existing Python project.

**What you can do:** Use a clean directory for running `stb new`.

## cookiecutter-failed

This error indicates that `stb new` could not create the repository. This is
currently expected as the repository that `stb new` tries to use is not set up.

**What you can do:** Manually create your theme's codebase, using existing
themes like [Furo] or [pydata-sphinx-theme] as the base for that.

[furo]: https://github.com/pradyunsg/furo/
[pydata-sphinx-theme]: https://github.com/pydata/pydata-sphinx-theme/

## fetch-sample-docs-clone-failed

This error indicates that the sample documentation repository could not be
cloned. This can happen for many reasons, some of which could be:

- `git` not being available
- Invalid reference being provided via `--ref`
- Network connectivity issues
- The sphinx-themes.org repository has moved

**What you can do:** Investigate the `git clone` failure, based on the logs
provided by git -- the specific action items will vary by failure mode.

## fetch-sample-docs-missing-directory

This error indicates that the requested subdirectory (e.g. `sample-docs/`) was
not found in the fetched repository at the given ref. This can happen if the
repository structure changed or if an incorrect `--ref` was supplied.

**What you can do:** Verify the repository and subdirectory exist (eg: by
inspecting the repository on GitHub).

## fetch-sample-docs-copy-failed

This error indicates that the sample documentation could not be copied to the
requested destination folder.

**What you can do:** Investigate the failure mentioned and resolve it.

## no-nodeenv

This error is raised by `stb npm` when the user tries to use it without creating
the nodeenv for the project.

**What you can do:** Run `stb compile` once, to create the nodeenv.

## autobuild-failed

This error is raised when `sphinx-autobuild` exits with an error, which is
typically caused by a fatal error or interrupt.

**What you can do:** Investigate why the Sphinx build failed. Typically, the
output for failure above this error will provide relevant information.
