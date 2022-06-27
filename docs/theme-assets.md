# Managing theme assets

The `sphinx-theme-builder` intentionally separates asset source files from the
compiled assets that are bundled with your theme. These generally fall into two
folders:

- "Asset sources" in `src/my_awesome_theme/assets`

  The source files used for generating the theme's actual stylesheet/JavaScript
  files (e.g. `.scss` files, `.ts` files).

- "Compiled static assets" in
  `src/my_awesome_theme/theme/my-awesome-theme/static`

  These are the files that will be used by Sphinx (e.g. `.css` files generated
  from `.scss`, `.js` files after transpiling and bundling).

## Compiling assets

As described in the {doc}`build-process` document, themes are expected to
compile assets through a NodeJS-based build system with `npm run-script build`
being the entrypoint for it.

During theme development, it is expected that theme authors will not need to
invoke npm manually. Instead, when you want to compile the theme's assets,
you'll run:

```sh-session
$ stb compile
```

This will handle all the details of fetching NodeJS, the npm dependencies and
other running the build via npm.

When previewing documentation using `stb serve`, this command will run prior to
rebuilding the documentation. This means that your theme development workflow
will not require manually invoking the rebuild. The live-reloading server
ignores assets in the static folder, so generating files there does not trigger
a re-build loop.

## Example: Webpack-based asset generation

For an example, we'll use Furo's 2022.06.21 release. That version of the Furo
theme uses a Webpack based asset generation pipeline, for compiling Sass and JS
source assets into generated CSS and JS assets.

The relevant files for this setup are:

- <https://github.com/pradyunsg/furo/blob/2022.06.21/pyproject.toml>
  - Configures Sphinx Theme Builder
  - Declares Python metadata + dependencies
  - Notice `additional-compiled-static-assets` in there
- <https://github.com/pradyunsg/furo/blob/2022.06.21/package.json>
  - Declares JS build dependencies
  - Declares entrypoint for `npm run-script build` as `webpack`
- <https://github.com/pradyunsg/furo/blob/2022.06.21/webpack.config.js>
  - Configures Webpack to compile the assets into the relevant location
    - transpile Sass files into CSS and run PostCSS on it
    - bundle multiple JS files into a single JS file
- <https://github.com/pradyunsg/furo/blob/2022.06.21/postcss.config.js>
  - Configure PostCSS to run autoprefixer
