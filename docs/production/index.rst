Production
==========

Taking a bootstack app from your machine to your users — the command-line tools,
packaging a standalone executable, diagnosing problems, and persisting
application settings.

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: :octicon:`terminal;1.5em;sd-mr-1` CLI & Tooling
      :link: cli
      :link-type: doc

      The `bootstack` command — scaffold, run, add components, and explore the
      framework.

   .. grid-item-card:: :octicon:`package;1.5em;sd-mr-1` Distribution
      :link: distribution
      :link-type: doc

      Package a project into a standalone executable with PyInstaller.

   .. grid-item-card:: :octicon:`zap;1.5em;sd-mr-1` Hot Reload
      :link: hot-reload
      :link-type: doc

      Edit and save to update the running app in place with `bootstack dev`.

   .. grid-item-card:: :octicon:`bug;1.5em;sd-mr-1` Debugging
      :link: debugging
      :link-type: doc

      The `doctor` health check, full tracebacks, and the exceptions to expect.

   .. grid-item-card:: :octicon:`gear;1.5em;sd-mr-1` Application Settings
      :link: app-settings
      :link-type: doc

      Configure the app at construction and persist preferences across runs.

.. toctree::
   :hidden:
   :maxdepth: 1

   cli
   distribution
   hot-reload
   debugging
   app-settings
