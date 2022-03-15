# Specification

Use Visual Studio Code to edit the specification files in the `source` directory.

For auto-reload and live-preview functionality, do the following:

- Run `make watch` - runs a watcher to detect changes in files with the `.adoc` extension. Outputs build files to `../build`
- Right-click on the `../build/index.html` file and click "Open Preview"

Now when you make changes to any `.adoc` files, it will automatically rebuild and reload the preview window.

> :warning: In some instances, the preview window will not reload automatically. To get around this, install the Visual Studio Code extension "Live Preview" by Microsoft. This extension provides a manual refresh button if it does not refresh automatically.
