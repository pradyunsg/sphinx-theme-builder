# Changelog

## v0.2.0

- A non-beta release for 0.2.0, that's compatible with older Python versions.

## 0.2.0b2

- Adopt the newer copy of `copyfileobj_with_hashing`
- Correctly encode `RECORD` hashes
- Document a previously undocumented error case
- Document the `--pdb` flag
- Improve documentation to pass nit-picks
- Improve the `autobuild-failed` documentation
- Use tomllib on Python 3.11+

## 0.2.0b1

- Add `--host` to `stb serve`.
- Document a theme asset management approach.
- Fix the generator value.
- Generate a `package-lock.json` file, if it does not exist.
- Switch to `pyproject-metadata` (from `pep621`).

## 0.2.0a15

- Add `--pdb` flag to `stb serve`.
- Accept more values for `STB_USE_SYSTEM_NODE`, error out on invalid ones.
- Add `STB_RELAX_NODE_VERSION_CHECK`.
- Fix typing-related import for Python 3.7 compatibility.
- Document all errors in the error index, describing what the user can do.
- Fix project source URL in metadata.
- Improve the getting started tutorial.
- Tweak how links are presented in errors.

## 0.2.0a14

- Don't pin the upper Python version.
- Present the traceback on Sphinx failures.
- Update error message for `nodeenv-creation-failed`
- Quote the `sys.executable`.
- Fix mis-formatted README opening.
- Back to development.

## 0.2.0a13

- Simplify system node usage logic.
- Use the correct binary directory on Windows.
- Reducing the size of the generated nodeenv.
- Add TODOs to the tutorial, to reflect it is incomplete.

## 0.2.0a12

- Fix Windows compatibility.

## 0.2.0a11

- Fix Python 3.7 compatibility.
- Fix handling of missing `node` executable on system.
- Explicitly declare the LICENSE.

## 0.2.0a10

- Fix improper RECORD file generation.

## 0.2.0a9

- Try to fix improper RECORD file generation.

## 0.2.0a8

- Add `stb compile --production`
- Improve documentation on what the project layout is.

## 0.2.0a7

- Allow setting alternative theme name.
- Enable users to specify custom "additional compiled static assets".
- Present error when npm is not found.
- Present more context when deciding on using `system` nodeenv.
- Run `nodeenv` with rich traceback installed.
- Search `PATH` for executables to run in nodenv.
- Suppress exception stack from click.

## 0.2.0a6

- Include parent paths of compiled files, when computing files for the wheel
  archive.
- Fix release version management.

## 0.2.0a5

- Include setuptools as a dependency.

## 0.2.0a4

- Add `stb npm` command, to make it easier to run npm within the nodeenv.
- Properly handle `nodeenv` and CLI colours.
- Get `node-version` from project configuration.
- Use the `node` from PATH, if it matches the required version
- Handle aborts coming out of click.
- Handle unclean exits in `build`.

## 0.2.0a3

- Improve `stb serve`.
- Improve handling and presentation of errors from `main`.
- Run project structure validation in more situations.
- Consolidate compiled asset calculation.
- Add a direct dependency on `nodeenv`.

## 0.2.0a2

- Update the paths that source assets are stored in.
- Correctly handle `[project]` in the error output.

## 0.2.0a1

Initial release.
