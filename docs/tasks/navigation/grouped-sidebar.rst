Grouped sidebar
===============

Authored pages chunked into labeled sections — the Settings window. The pages
work exactly like a :doc:`single-tier app <single-tier>`; section labels and
dividers add visual structure when the destinations fall into categories.

.. image:: /_static/examples/navigation-grouped-sidebar-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: Grouped settings sidebar — light theme

.. image:: /_static/examples/navigation-grouped-sidebar-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: Grouped settings sidebar — dark theme

How it works
------------

`add_header(text)` adds a quiet, non-interactive section label; `add_separator()`
adds a divider. The pages added after a header read as belonging to it — the
label's color and the extra top margin carry the grouping, so the items stay
flush (no indentation).

.. code-block:: python

   shell.add_header("Account")
   with shell.add_page("profile", text="Profile", icon="person"):
       ...
   shell.add_header("Notifications")
   with shell.add_page("email", text="Email", icon="envelope"):
       ...

Group **consistently** — put everything under headers, rather than sprinkling
loose top-level items among sections. A pinned footer item is the conventional
exception.

Example
-------

.. literalinclude:: ../../examples/navigation/grouped_sidebar.py
   :language: python
   :linenos:

When to use
-----------

Use a grouped sidebar when authored pages fall into a few clear categories. If
you find yourself wanting a section that *collapses* to hide its items, that is a
content concern rather than navigation — compose an
:class:`Accordion <bootstack.widgets.accordion.Accordion>` inside a
:doc:`custom sidebar <custom-sidebar>`. If a "section" is really a long list of
records, use :doc:`master-detail-list`.
