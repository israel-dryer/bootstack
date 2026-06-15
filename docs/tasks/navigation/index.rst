Navigation patterns
====================

:class:`AppShell <bootstack.AppShell>` assembles a few building blocks —
authored pages, data-bound providers, and an optional workspace rail — into the
navigation shape your app needs. This is a catalog of the common shapes: find the
one that matches what you're building, then copy its worked example.

Every pattern is authored with the same small API, so you can start simple and
grow: a flat list of pages becomes a grouped one becomes a multi-section app with
a rail, without rewriting what you have.

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Single-tier app
      :link: single-tier
      :link-type: doc

      A flat sidebar of top-level pages — the everyday dashboard. Use when you
      have a handful of destinations and no sub-grouping.

   .. grid-item-card:: Grouped sidebar
      :link: grouped-sidebar
      :link-type: doc

      Pages chunked into labeled sections — the Settings window. Use when the
      destinations fall into clear categories.

   .. grid-item-card:: Master–detail (list)
      :link: master-detail-list
      :link-type: doc

      A list drives a detail view — the email inbox. Use when the sidebar is a
      list of records and the content shows one at a time.

   .. grid-item-card:: Master–detail (tree)
      :link: master-detail-tree
      :link-type: doc

      A hierarchy drives a detail view — the file explorer. Use when records nest
      under parents.

   .. grid-item-card:: Workspaces (rail)
      :link: workspaces
      :link-type: doc

      Multiple sections behind an icon rail — a mail + calendar suite. Use when
      the app has distinct areas, each with its own sidebar.

   .. grid-item-card:: Custom sidebar
      :link: custom-sidebar
      :link-type: doc

      A bespoke sidebar you build by hand — a filter panel. The escape hatch when
      none of the providers fit.

.. seealso::

   For the full `AppShell` API — every method, property, and option — see the
   :doc:`AppShell widget guide </widgets/appshell>`. For lower-level page
   switching without a sidebar, see :doc:`PageStack </widgets/pagestack>` and
   :doc:`Tabs </widgets/tabs>`.

.. toctree::
   :hidden:

   single-tier
   grouped-sidebar
   master-detail-list
   master-detail-tree
   workspaces
   custom-sidebar
