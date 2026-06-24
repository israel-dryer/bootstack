CLI & Tooling
=============

bootstack ships a command-line tool, `bootstack`, for scaffolding projects,
running them, packaging a standalone executable, and exploring the framework. It
is installed with the package; run `bootstack --help` for a summary, or
`bootstack <command> --help` for any command's options.

Two global flags apply to every command:

- `--version` — print the installed bootstack version.
- `-v`, `--verbose` — print a full traceback on error (otherwise errors are a
  one-line message). See :doc:`debugging`.

Creating a project
------------------

`bootstack start <name>` scaffolds a new project — an entry point, a
`bootstack.toml` manifest, and starter views or pages.

.. code-block:: bash

   bootstack start MyApp                           # single-view app (basic)
   bootstack start MyApp --template appshell       # sidebar-navigation app
   bootstack start MyApp --template appshell --nav workspaces

Key options:

.. list-table::
   :header-rows: 1
   :widths: 24 76

   * - Option
     - Effect
   * - `--template {basic,appshell}`
     - `basic` is a single-window app; `appshell` adds a navigation shell.
       Default `basic`.
   * - `--nav {single,grouped,master-detail,workspaces}`
     - Navigation style for the `appshell` template — a flat sidebar, grouped
       sections, a record list/detail, or a workspace rail. Default `single`;
       ignored for `basic`. The scaffold includes a menu bar, command bar, and
       status bar you can trim.
   * - `--theme <name>`
     - Initial theme (e.g. `bootstrap-dark`). Default `bootstrap-light`.
   * - `--container {grid,pack}`
     - Default layout container for `basic` views. Default `grid`; ignored for
       `appshell`.
   * - `--simple`
     - Minimal project — no assets directory or build configuration.
   * - `--dir <path>`
     - Target directory. Defaults to `./<name>`.

The navigation styles mirror the :doc:`/tasks/navigation/index` patterns, so the
scaffold is a working starting point for each shape.

Running a project
-----------------

`bootstack run` finds the project's `bootstack.toml` (searching parent
directories), puts `src/` on the path, and runs the entry point:

.. code-block:: bash

   bootstack run            # run the project in the current directory
   bootstack run path/to/project

Adding components
-----------------

`bootstack add <kind> <Name>` scaffolds a new component and tells you how to wire
it in. The kinds:

.. code-block:: bash

   bootstack add page DashboardPage      # appshell projects — a navigable page
   bootstack add view SettingsView       # basic projects — a view
   bootstack add dialog ConfirmDialog    # a custom dialog
   bootstack add i18n --languages en es  # translatable-text scaffolding

`add page` is for `appshell` projects and `add view` for `basic` projects; each
generates a builder function (`def build_<name>(): ...`) and prints the lines to
paste into `main.py`. See :doc:`/tasks/composing-with-builders` for the pattern.

Packaging
---------

Two commands turn a project into a standalone executable, covered in full in
:doc:`distribution`:

.. code-block:: bash

   bootstack promote --pyinstaller   # add build config + a PyInstaller spec
   bootstack build                   # produce dist/<App> via PyInstaller

Diagnostics
-----------

`bootstack doctor` checks your environment and project (Python and Tcl/Tk
versions, the manifest and entry point, the template layout, and — once
promoted — PyInstaller and the spec file). See :doc:`debugging`.

.. code-block:: bash

   bootstack doctor

Exploring the framework
-----------------------

Three commands open interactive windows — no project required:

.. code-block:: bash

   bootstack gallery     # a live tour of every widget, theme, and layout
   bootstack icons       # browse the bundled Bootstrap Icons (click to copy a name)
   bootstack appicon     # design an application icon and export .ico/.icns/.png

The icon designer pairs with :doc:`/tasks/application-icons`.

See also
--------

- :doc:`distribution` — the packaging workflow and `bootstack.toml` `[build]`.
- :doc:`debugging` — `doctor`, verbose errors, and common problems.
- :doc:`/getting-started/quickstart` — your first app.
