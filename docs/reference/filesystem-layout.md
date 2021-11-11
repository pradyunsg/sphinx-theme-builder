# Filesystem Layout

Sphinx Theme Builder requires the themes to follow a fairly specific
project layout and structure. This standard structure is what allows
this tool to provide a sensible build pipeline, which in-turn enables
all the nice quality-of-life things like `stb serve`.

## How it looks

```yaml
- README.md
- LICENSE
- package.json # For Javascript-based build tooling.
- pyproject.toml # For Python package metadata and tooling.
- src:
    - my_amazing_theme: # The importable Python package (notice underscores)
        - __init__.py
        - [other Python files]
        - theme: # HTML templates
            - my-amazing-theme:
                - [various .html pages]
                - static
                  - [any static assets that don't need to be compiled, like images]
        - assets: # Static assets, SASS and JS.
            - [static assets that need to be compiled, possibly within folders]
            - styles:
                - index.sass # Compiled into the final CSS file.
                - [other Sass / SCSS files]
            - scripts:
                - my-amazing-theme.js # Compiled into the final JS file.
                - [other JS files]
```

## Auto-generated folders

The following folders will be auto-generated when you compile your theme.
Consider adding them to your `.gitignore`:

- `.nodeenv` - The `npm` installation that is used to compile your theme's assets.
- `node_modules` - The `node` packages that were installed to compile your theme's assets.
- `src/theme/<my-awesome-theme>/static/styles` - The compiled CSS assets for your theme
- `src/theme/<my-awesome-theme>/static/scripts` - The compiled JS assets for your theme

## What is needed

This section describes what needs to be done in the various files in the
skeleton of the project. These are things that are checked when
performing the build, unless otherwise noted.

```{todo}
Flesh this out.
```
