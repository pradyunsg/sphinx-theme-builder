# Build Process

```{todo}
Describe how the theme source tree -> distribution process works. Note
the knobs that the theme authors have in it.
```

## Using `package-lock.json`

By default, this tool does not generate a `package-lock.json` when you install
your Node environment. This avoids unexpected changes to the package lockfile.

However, it is strongly encouraged to generate a `package-lock.json` file in
order to stabilize the JavaScript versions that are installed when somebody
builds your theme locally.

To do so, run the following command after installing this theme locally for the
first time:

```
stb npm install --include=dev
```

This will generate a `package-lock.json` file that you can check in to your
repository.
