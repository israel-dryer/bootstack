Custom sidebar
==============

A bespoke sidebar you build by hand — a faceted filter panel, a tool palette, a
layer list. The escape hatch for when the sidebar isn't navigation at all, so none
of the built-in providers fit.

.. image:: /_static/examples/navigation-custom-sidebar-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: Custom filter sidebar — light theme

.. image:: /_static/examples/navigation-custom-sidebar-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: Custom filter sidebar — dark theme

How it works
------------

`panel()` claims the sidebar as a blank container and returns it as a context
manager — fill it with any widgets. You then drive the content area yourself
through `shell.content` (also a container), typically by binding widgets to a
:class:`Signal <bootstack.Signal>`. There is no provider cascade and no
compaction.

.. code-block:: python

   with shell.panel():
       bs.Label("Filters", font="heading-md")
       bs.SelectButton(options=["All", "Electronics", "Home"], signal=category)

   with shell.content:
       bs.Label("Results", font="heading-lg")
       bs.Label(textsignal=results)

Because there are no pages, `navigate()` does not apply — the content is whatever
you put there and update.

Example
-------

.. literalinclude:: ../../examples/navigation/custom_sidebar.py
   :language: python
   :linenos:

When to use
-----------

Reach for a custom sidebar only when `add_page`, `list_nav`, and `tree_nav`
genuinely can't express what you need — a sidebar that isn't a navigation list.
If you want collapsible sections of *navigation*, prefer a
:doc:`grouped sidebar <grouped-sidebar>` (or an
:class:`Accordion <bootstack.widgets.accordion.Accordion>` inside the panel for
collapsible *content*). For records, use a :doc:`list <master-detail-list>` or
:doc:`tree <master-detail-tree>` master–detail.
