# Filesystem Layout

Sphinx Theme Builder requires the themes to follow a fairly specific project
layout and structure. This standard structure is what allows this tool to
provide a sensible build pipeline, which in-turn enables the nice
quality-of-life things like `stb serve`.

## How it looks

```yaml
- .gitignore # The theme should be under version control with git
- README.md
- LICENSE
- package.json # For Javascript-based build tooling.
- pyproject.toml # For Python package metadata and tooling.
- src:
    - my_amazing_theme: # The importable Python package (notice underscores)
        - __init__.py
        - [other Python files]
        - theme: # HTML templates
            - my_amazing_theme:
                - [various .html pages]
                - static - [any static assets that don't need to be compiled,
                  like images]
        - assets: # Static assets, SASS and JS.
            - [static assets that need to be compiled, possibly within folders]
            - styles:
                - index.sass # Compiled into the final CSS file.
                - [other Sass / SCSS files]
            - scripts:
                - my-amazing-theme.js # Compiled into the final JS file.
                - [other JS files]
```

## Need for version control

Sphinx Theme Builder does not enforce the use of Git but, as part of the build
process, it will exclude any files that are excluded from Git's tracking using
any of the supported mechanisms (typically, a `.gitignore` file in the
repository root). This information is queried as part of the source distribution
generation process.

## Auto-generated folders

The following folders will be auto-generated when the theme's assets are
compiled. Add them to the project's `.gitignore`:

- `.nodeenv` - The NodeJS (+ `npm`) installation that is used to compile the
  theme's assets.
- `node_modules` - The NodeJS packages that are installed for use, to compile
  the theme's assets.
- `src/<my_amazing_theme>/theme/<my_amazing_theme>/static/styles` - The compiled CSS assets for the
  theme
- `src/<my_amazing_theme>/theme/<my_amazing_theme>/static/scripts` - The compiled JS assets for the
  theme

## How to get this right

Nearly everything about the filesystem layout and the contents of the various
configuration files are validated, as part of the build process. This means that
you can get the layout and contents of the files correct by ensuring that the
build of the theme succeeds, when using Sphinx Theme Builder.

This typical workflow for doing this looks something like:

1. Update the `build-backend` for the theme to Sphinx Theme Builder.

   ```{code-block} toml
   :name: stb-pyproject-config
   :caption: pyproject.toml

   [build-system]
   requires = ["sphinx-theme-builder >= 0.2.0a14"]
   build-backend = "sphinx_theme_builder"
   ```

1. Run `stb package` in the same directory as the `pyproject.toml` file.
1. Fix the error presented.
1. Repeat the above two steps, that until the `stb package` command succeeds.
1. And.. done!
