Single-tier app
===============

A flat sidebar of top-level destinations — the everyday "dashboard" app. Each
sidebar item is an authored page; selecting it shows that page's content. With a
single set of pages, no workspace rail appears.

.. image:: /_static/examples/navigation-single-tier-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: Single-tier dashboard app — light theme

.. image:: /_static/examples/navigation-single-tier-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: Single-tier dashboard app — dark theme

How it works
------------

`add_page(key, *, text, icon)` registers a sidebar item and its content page
together, and returns a context manager — widgets created inside the ``with``
block are parented to that page. `add_footer_page()` pins an item (Settings,
Account) to the bottom of the sidebar. `navigate(key)` selects the starting page.

.. code-block:: python

   with shell.add_page("overview", text="Overview", icon="speedometer2"):
       bs.Label("Overview", font="heading-lg")
   shell.navigate("overview")

Example
-------

.. literalinclude:: ../../examples/navigation/single_tier.py
   :language: python
   :linenos:

When to use
-----------

Reach for the single-tier app when you have a handful of independent
destinations and no need to sub-group them. If the destinations fall into clear
categories, add section labels — see :doc:`grouped-sidebar`. If the sidebar is
really a list of records (messages, devices), use :doc:`master-detail-list`
instead. If the app has several distinct areas each with their own sidebar, give
each a workspace — see :doc:`workspaces`.
