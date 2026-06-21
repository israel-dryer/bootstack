Spacer
======

A flexible break that pushes its neighbors apart inside a
:class:`Row <bootstack.Row>` or :class:`Column <bootstack.Column>`. By default it
absorbs the leftover space along the stacking axis, so items before it cluster at
the start and items after it cluster at the end.

.. image:: /_static/examples/spacer-hero-light.png
   :class: bs-screenshot-light
   :alt: Spacer — light theme

.. image:: /_static/examples/spacer-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Spacer — dark theme

Usage
-----

Where ``horizontal_items`` / ``vertical_items`` arrange the *whole* group, a
Spacer opens a gap at a *single* point — drop one into a toolbar to send the
trailing buttons to the far edge, no nesting required.

Pushing items apart
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   with bs.Row(gap=4, horizontal="stretch"):
       bs.Button("New")
       bs.Button("Open")
       bs.Spacer()                       # everything after is pushed right
       bs.Button("Settings")
       bs.Button("Profile")

Fixed gaps
~~~~~~~~~~

``Spacer(size=N)`` is a rigid N-pixel gap rather than flexible slack — use it for
a deliberate, fixed separation between clusters.

.. code-block:: python

   with bs.Row(gap=4):
       bs.Button("One")
       bs.Spacer(size=48)                # a fixed 48 px gap
       bs.Button("Two")
       bs.Spacer(size=48)
       bs.Button("Three")

.. image:: /_static/examples/spacer-fixed-light.png
   :class: bs-screenshot-light
   :alt: Spacer fixed gaps — light theme

.. image:: /_static/examples/spacer-fixed-dark.png
   :class: bs-screenshot-dark
   :alt: Spacer fixed gaps — dark theme

Sharing space by weight
~~~~~~~~~~~~~~~~~~~~~~~~~

Several flexible spacers split the leftover space in proportion to their
``weight=``. With ``weight=1`` and ``weight=2``, the second gap is twice the
first.

.. code-block:: python

   with bs.Row(gap=4, horizontal="stretch"):
       bs.Button("Left")
       bs.Spacer(weight=1)
       bs.Button("Center")
       bs.Spacer(weight=2)               # twice the slack of the first
       bs.Button("Right")

.. image:: /_static/examples/spacer-weighted-light.png
   :class: bs-screenshot-light
   :alt: Spacer weighted — light theme

.. image:: /_static/examples/spacer-weighted-dark.png
   :class: bs-screenshot-dark
   :alt: Spacer weighted — dark theme

Pushing a footer down
~~~~~~~~~~~~~~~~~~~~~~~

In a Column, a Spacer drives a footer to the bottom without fixing the column
height.

.. code-block:: python

   with bs.Column(gap=6, horizontal_items="stretch"):
       bs.Label("Title", font="heading-md")
       bs.Label("Body content.")
       bs.Spacer()                       # pushes the footer to the bottom
       bs.Button("Save", accent="primary")

.. image:: /_static/examples/spacer-column-light.png
   :class: bs-screenshot-light
   :alt: Spacer in a column — light theme

.. image:: /_static/examples/spacer-column-dark.png
   :class: bs-screenshot-dark
   :alt: Spacer in a column — dark theme

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:class:`Row <bootstack.widgets.stacks.Row>` and
:class:`Column <bootstack.widgets.stacks.Column>` — the containers a Spacer lives
in; their ``horizontal_items`` / ``vertical_items`` arrange the whole group,
where a Spacer opens a gap at one point.

API
---

The complete reference for :class:`Spacer <bootstack.Spacer>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Spacer

Full Example
------------

.. literalinclude:: ../../docs/examples/spacer.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
