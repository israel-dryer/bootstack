Distribution
============

bootstack packages a project into a standalone executable with `PyInstaller`, so
your users can run the app without installing Python. Packaging is a two-step
flow: **promote** the project once to add the build configuration, then **build**
whenever you want a fresh executable.

Promote, then build
-------------------

.. code-block:: bash

   bootstack promote --pyinstaller   # one time: add [build] + a PyInstaller spec
   bootstack build                   # produce the executable in dist/

`promote --pyinstaller` adds a `[build]` section to `bootstack.toml` and
generates `build/pyinstaller/app.spec`. It also checks that PyInstaller is
installed and warns if it is not — install it with `pip install pyinstaller`.
Pass `--force` to regenerate the build files if they already exist.

`build` reads the manifest, runs PyInstaller against the spec, and writes the
result to `dist/`. Use `--clean` to clear stale build artifacts first:

.. code-block:: bash

   bootstack build --clean

The output is a `dist/<AppName>/` folder containing the executable (the default),
or a single `dist/<AppName>` executable when `onefile` is set. The spec bundles
the framework's own assets — themes, icons, fonts, and locales — automatically.

The build configuration
-----------------------

Promotion adds a `[build]` table to `bootstack.toml`. The defaults suit most
apps; edit them to change how the executable is produced:

.. code-block:: toml

   [build]
   backend = "pyinstaller"   # the only backend today
   windowed = true           # a GUI app with no console window
   onefile = true            # one executable (false for a folder)
   hidden_imports = []        # modules PyInstaller misses — add ones your app needs
   excludes = []              # modules to leave out of the build

   [build.datas]
   include = [               # extra non-Python files to bundle (glob patterns)
       "assets/**",
   ]

Set `windowed = false` if your app should keep a console (useful while
debugging). `onefile` is the default — a single, tidy executable, though it
starts a little slower because it unpacks to a temporary directory on launch; set
`onefile = false` for a faster-starting folder. Anything your app reads at
runtime — images, data files — belongs in `[build.datas] include` so it ships
inside the executable.

`hidden_imports` is the usual fix when a packaged app fails to import a module
that worked while developing — PyInstaller's analysis can miss dynamically
imported packages, so list them here. `excludes` trims modules you do not need.

Going further
~~~~~~~~~~~~~

`[build]` covers the common options. For anything else PyInstaller supports —
extra binaries, custom hooks, UPX settings — edit the generated spec at
`build/pyinstaller/app.spec` directly. It is a standard `PyInstaller spec file
<https://pyinstaller.org/en/stable/spec-files.html>`_, regenerated only when you
run `bootstack promote --pyinstaller --force`.

The distribution icon
---------------------

`[build.icon]` sets the icon **embedded in the packaged executable** — what the
operating system shows for the program file, its Start-menu or Dock entry, and
pinned shortcuts. This is **not** the runtime window icon (the title bar and
taskbar icon of the *running* app), which you set in code with `App(icon=…)` or
`Window(icon=…)`. The two are independent settings.

Point `[build.icon]` at an existing icon file, or describe a glyph and let the
build render one:

.. code-block:: toml

   [build.icon]
   # A single file (used on whatever platform you build on)…
   path = "assets/app.ico"

   # …or per-platform artwork (each used only on its own platform):
   windows = "assets/app.ico"
   macos = "assets/app.icns"

   # …or a glyph, rendered in the host platform's format at build time
   # (colors must be hex — no theme is running during a build):
   glyph = "rocket"
   background = "#0d6efd"
   foreground = "#ffffff"
   radius = 0.22
   shape = "auto"

A build runs on one platform at a time (PyInstaller does not cross-compile), so
it only needs that platform's icon format — `.ico` on Windows, `.icns` on macOS.
A `windows`/`macos`/`linux` path wins over the generic `path` on its platform,
and a single `glyph` is rendered into the host's format automatically, so one
glyph works everywhere. If you set no icon at all, the build falls back to the
bundled bootstack icon.

For a consistent look, point the distribution icon and the runtime `App(icon=…)`
at the same artwork. The full story — runtime versus distribution icons, and the
`bootstack appicon` designer — is in :doc:`/tasks/application-icons`.

A typical workflow
------------------

.. code-block:: bash

   bootstack doctor                  # confirm the environment is build-ready
   bootstack promote --pyinstaller   # once, to set up packaging
   # edit bootstack.toml [build] if needed (onefile, icon, datas)
   bootstack build --clean           # produce dist/<App>

If a build fails or the packaged app misbehaves, :doc:`debugging` has a
troubleshooting checklist.

See also
--------

- :doc:`cli` — the full command reference.
- :doc:`/tasks/application-icons` — runtime and distribution icons.
- :doc:`debugging` — diagnosing build and runtime problems.
