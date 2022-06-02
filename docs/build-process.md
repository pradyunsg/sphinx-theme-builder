# Build Process

This document describes the build process of a theme, built using Sphinx Theme
Builder (`stb`). In other words, this document serves as an elaborate answer to
the question: "What happens when I run `stb compile` or `stb package`?"

(asset-generation)=

## Asset Generation

This is all that `stb compile` does.

### nodeenv creation

`stb` invokes {pypi}`nodeenv`, in a subprocess and creates an isolated
installation of NodeJS in a `.nodeenv` directory.

If a `.nodeenv` directory already exists, this step is skipped.

#### Getting the NodeJS binaries to use

nodeenv uses the NodeJS release files available at
<https://nodejs.org/download/release/>
(<https://unofficial-builds.nodejs.org/download/release/> for musl), for
creating the isolated installation. It is possible to configure it using [a
`~/.nodeenvrc` file][nodeenv-configuration] to change its behaviours, such as
whether it uses a pre-built binary or what mirror it downloads from.

By default, nodeenv will try to prefer to use pre-built binaries, if they're
available for the platform that the build is taking place on. If a pre-built
binary is not available, it tries to build NodeJS from source on the machine.

[nodeenv-configuration]: https://github.com/ekalinin/nodeenv#configuration

##### `STB_USE_SYSTEM_NODE`

`stb` looks at a `STB_USE_SYSTEM_NODE` environment variable when deciding how to
invoke `nodeenv`. If it is equal to `true`, `stb` will use ask nodeenv to use
the `node` executable available on `PATH`.

This functionality is primarily for software redistributors who have policies
against using prebuilt binaries from the NodeJS team, such as the ones that
`nodeenv` tries to use by default.

```{note}
The version of NodeJS provided by this mechanism _must_ match the version of
NodeJS in the theme's `pyproject.toml`.
```

### nodeenv validation

Once `stb` has a nodeenv available, it will run `node --version` using the
nodeenv's `node` and validate that it matches the requirements of the theme,

This serves as a validation check to ensure that the user does not incorrectly
use a broken nodeenv (in which case, `node` will fail to run) or a NodeJS
version that is incompatible with the theme (which can happen in some
situations). Even when the nodeenv was just created, this serves as a
sanity-check that the nodeenv that has been created is indeed functional and
valid.

### `npm install`

Once the nodeenv is created, the JS dependencies of the theme are installed by
running `npm install` using from the nodeenv. This will create a `node_modules`
directory containing these dependencies.

If a `node_modules` directory already exists and is newer than the
`package.json` file, this step is skipped.

### `npm run-script build`

With all the NodeJS dependencies of the theme installed, the NodeJS-based build
is performed by `npm` from the nodeenv. This build is done by using
`npm run-script build` which looks at the `"build"` key in the `"scripts"`
section of `package.json`.

For a package that uses [Webpack] for performing their JS build, this would mean
that the `package.json` would look something like:

```json
{
  "devDependencies": {
    "webpack": "...",
    "webpack-cli": "..."
  },
  "scripts": {
    "build": "webpack"
  }
}
```

This command is expected to generate the compiled assets for the theme. If the
theme's `build` command is being executed, everything that `stb` does is working
correctly.

## Python Packaging stuff

`stb package` dispatches the task of performing the build to the {pypi}`build`
project, by invoking it in a subprocess. The build project orchestrates the
details of the build process and ends up invoking `stb`'s build logic, in the
appropriate manner.

The build project generates a source distribution, unpacks it and builds a wheel
from the unpacked source distribution.

## Source Distribution

For generating the source distribution, `stb` will generate a tarball that
contains files from the `src/` directory of the project. Certain files are not
included in this tarball, based on the following rules:

- Exclude hidden files.
- Exclude `.pyc` files.
- Exclude compiled assets.
- Exclude files that are excluded from version control (only git is supported).

## Wheel Distribution

For generating the wheel distribution, `stb` will generate the theme's assets in
production mode (using the {ref}`asset-generation` process described above).
Once this is generated, `stb` will generate a wheel file containing the package
metadata and all the files in the `src/` directory.

```{caution}
It is expected that wheels would only be generated from unpacked source
distributions. Attempting to generate a wheel from the source tree directly
may result in incorrect contents in the wheel.
```
