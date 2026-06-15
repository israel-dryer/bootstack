Debugging
=========

When something goes wrong — at startup, during a build, or while your app runs —
bootstack gives you a health check, full tracebacks on demand, and a small set of
clearly-named exceptions that point at the cause.

Checking your environment
-------------------------

`bootstack doctor` is the first thing to run when a project will not start or
build. It inspects three areas and prints an `[OK]` / `[WARN]` / `[FAIL]` line
for each:

- **Environment** — the Python and Tcl/Tk versions and the installed bootstack
  version.
- **Project** — that `bootstack.toml` exists and parses, the entry point file is
  present, and the directory layout matches the template (`pages/` for an
  appshell project, `views/` for a basic one).
- **Packaging** — for a promoted project, that PyInstaller is importable and the
  spec file exists.

.. code-block:: bash

   bootstack doctor

It exits non-zero if anything **failed** (a missing entry point, a parse error),
and zero when only warnings remain — so it works in a CI check.

Full tracebacks
---------------

By default the CLI prints a one-line error and a hint. Add `-v` / `--verbose` to
any command to see the complete Python traceback:

.. code-block:: bash

   bootstack run --verbose

For your own app, `bootstack run` inherits the entry point's standard output, so
`print()` and the `logging` module work as usual while you develop.

Exceptions you may see
----------------------

bootstack raises a small family of exceptions, all subclasses of
:class:`~bootstack.errors.BootstackError`, so you can catch the base type to
handle any of them:

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Exception
     - Usually means
   * - :class:`~bootstack.errors.UnknownEventError`
     - `widget.on("name", …)` used an event name the widget does not define.
       Check the spelling against :doc:`/reference/events`.
   * - :class:`~bootstack.errors.ParentResolutionError`
     - A widget could not find its parent — typically a widget created outside
       any `with` container block, or after its container was destroyed.
   * - :class:`~bootstack.errors.DuplicateIdError`
     - A data source received two records with the same id. Give each record a
       unique id field.
   * - :class:`~bootstack.errors.SerializationError`
     - A `Store` or file-backed data source was handed a value that is not
       JSON-serializable. Store plain data (str, number, bool, list, dict).

The full reference is :doc:`/api-reference/errors`.

Build and packaging problems
----------------------------

If `bootstack build` fails or the packaged app misbehaves, work through this
checklist:

- Run `bootstack doctor` — it flags a missing entry point, an absent PyInstaller,
  or a missing spec file.
- Regenerate a stale or corrupt spec with `bootstack promote --pyinstaller --force`.
- Confirm `[build.icon]` colors are **hex** (e.g. `#0d6efd`), not theme tokens —
  no theme is running during a build to resolve a token.
- Make sure `[build.datas] include` patterns match the files your app reads at
  runtime; anything missing won't be inside the executable.
- Clear stale artifacts with `bootstack build --clean`.
- A *file not found* at runtime in a packaged app almost always means a data file
  wasn't bundled — add it to `[build.datas]`.

See also
--------

- :doc:`cli` — `doctor`, `run`, and the verbose flag.
- :doc:`distribution` — the build configuration these problems relate to.
- :doc:`/api-reference/errors` — the exception types in full.
