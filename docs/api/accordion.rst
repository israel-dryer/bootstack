Accordion
=========

A list of collapsible sections, optionally limited to one open at a time.
Each section is an :class:`Expander <bootstack.widgets.expander.Expander>`
added via ``add()``.

.. code-block:: python

   acc = bs.Accordion()
   with acc.add("Introduction", expanded=True):
       bs.Label("First section.")
   with acc.add("Details"):
       bs.Label("Second section.")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/accordion-light.png"
        alt="Accordion demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/accordion-dark.png"
        alt="Accordion demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

Usage
-----

Basic Accordion
~~~~~~~~~~~~~~~

``add(title)`` returns an ``AccordionSection`` context manager. Place child
widgets inside it. By default only one section can be open at a time —
opening a second one collapses the first.

.. code-block:: python

   acc = bs.Accordion()
   with acc.add("Introduction", expanded=True):
       bs.Label("First section body.")
   with acc.add("Details"):
       bs.Label("Opening this collapses Introduction.")
   with acc.add("Summary"):
       bs.Label("Third section.")

Multiple open at once
~~~~~~~~~~~~~~~~~~~~~

``allow_multiple=True`` lets any number of sections be open simultaneously.

.. code-block:: python

   acc = bs.Accordion(allow_multiple=True)
   with acc.add("Section A", expanded=True):
       bs.Label("A is open.")
   with acc.add("Section B", expanded=True):
       bs.Label("B is also open.")

Prevent full collapse
~~~~~~~~~~~~~~~~~~~~~

``allow_collapse_all=False`` keeps at least one section expanded at all
times. The first section added is expanded by default.

.. code-block:: python

   acc = bs.Accordion(allow_collapse_all=False)
   with acc.add("Always one open"):
       bs.Label("Cannot be the last one closed.")

Separators
~~~~~~~~~~

``show_separators=True`` (default) draws a divider line between sections.
Set ``show_separators=False`` to remove the dividers.

.. code-block:: python

   acc = bs.Accordion(show_separators=False)
   with acc.add("Alpha", expanded=True):
       bs.Label("Body.")
   with acc.add("Beta"):
       bs.Label("Body.")

Border
~~~~~~

``show_border=True`` (default) wraps the entire accordion in a bordered
frame. Set ``show_border=False`` to render without an outer border.

.. code-block:: python

   acc = bs.Accordion(show_border=False)
   with acc.add("One", expanded=True):
       bs.Label("No outer border.")
   with acc.add("Two"):
       bs.Label("Body.")

Accent
~~~~~~

``accent=`` applies a color token to every section header.
Valid values: ``'primary'``, ``'secondary'``, ``'info'``, ``'success'``,
``'warning'``, ``'danger'``, ``'default'``.

.. code-block:: python

   acc = bs.Accordion(accent="primary")
   with acc.add("Features", expanded=True):
       bs.Label("Feature list.")
   with acc.add("Pricing"):
       bs.Label("Pricing details.")

Icons
~~~~~

Pass ``icon=`` to ``add()`` to display an icon to the left of the section
title.

.. code-block:: python

   acc = bs.Accordion(accent="info")
   with acc.add("Documents", icon="folder"):
       bs.Label("Files here.")
   with acc.add("Images", icon="image"):
       bs.Label("Images here.")
   with acc.add("Music", icon="file-music"):
       bs.Label("Music here.")

Section layout
~~~~~~~~~~~~~~

Each section body supports the same ``layout=``, ``gap=``, ``fill_items=``,
and other layout kwargs as a standalone
:class:`Expander <bootstack.widgets.expander.Expander>`.

.. code-block:: python

   acc = bs.Accordion()
   with acc.add("Form", layout="grid", columns=["auto", 1],
                gap=8, sticky_items="ew"):
       bs.Label("Name")
       bs.TextField()
       bs.Label("Email")
       bs.TextField()

Managing sections
~~~~~~~~~~~~~~~~~

.. code-block:: python

   acc = bs.Accordion()
   with acc.add("Alpha", expanded=True):
       bs.Label("Body.")

   acc.expand("expander_0")     # expand by auto-assigned key
   acc.collapse("expander_0")
   acc.expand_all()
   acc.collapse_all()
   acc.keys()                   # tuple of all section keys in order

Events
~~~~~~

``on_change()`` fires whenever any section expands or collapses.

.. code-block:: python

   acc = bs.Accordion()

   acc.on_change(lambda e: print("section changed"))

   # Stream (chainable)
   acc.on_change().listen(lambda e: print("changed"))

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`Card <bootstack.widgets.card.Card>` and
:class:`GroupBox <bootstack.widgets.groupbox.GroupBox>` are non-collapsible
containers.

API
---

.. autoclass:: bootstack.widgets.expander.Accordion
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/accordion.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs