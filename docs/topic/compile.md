# Compiling assets

The `sphinx-theme-builder` intentionally separates asset source files from the compiled assets that are bundled with your theme.
These generally fall into two folders:

- `src/{theme-name}/assets` - the source files for your assets (e.g. `.scss` files)
- `src/{theme-name}/theme/{theme-name}/static` - the compiled assets (e.g., `.css` files generated from `.scss`).

## Compile your assets

To compile your source files into static assets and bundle them with your site, run this command:

```
stb compile
```

This will execute everything in any `webpack` file that you use to compile the theme, and insert the appropriate assets in your theme's `static` folder.

```{note}
When you preview your documentation with `stb serve`, asset compilation will automatically happen any time you change a source file.
The re-build trigger will ignore the compiled asset folders (e.g., `...static/`) so that generating these files does not automatically trigger a re-build loop.
``` 

## Add extra assets to compile

The `sphinx-theme-builder` comes with two kinds of assets to compile: `style` assets (for `.scss`) and `script` assets (for `.js`).

If you'd like to compile and bundle other assets with your theme (for example, Sphinx translation files), here is a rough workflow:

1. **Define a new source file folder in `assets`**. This is where the source files for your new assets will live.
2. **Add an extra compilation step to your `webpack` configuration.** Your webpack configuration is a JavaScript file, so there is a lot of flexibility in what you can do. For example, you can [use the `child_process` config](https://nodejs.org/api/child_process.html#child_processexeccommand-options-callback) to execute arbitrary shell scripts as part of your build.
   The below code demonstrates how you would call a Python script as part of your build:

   ```js
   const { exec } = require("child_process");
   exec("python path/to/a/script.py");
   ```
   
   The result of this step should place compiled assets somewhere in your `src/{theme-name}/theme/{theme-name}/static` folder.
3. **Configure `sphinx-theme-builder` to use these assets**. You should use the `additional-compiled-static-assets` key and pass a list of files and folders that will be created at compilation time.
   These files should be **relative to your `static/` folder.
   For example, the following configuration adds two additional compiled static assets: an `.html` file and a folder called `locales/`.

   ```toml
   [tool.sphinx-theme-builder]
   ...
   additional-compiled-static-assets = [
     "sbt-webpack-macros.html",
     "locales/"
   ]
   ...
   ```
