ToggleGroup
===========

A group of toggle buttons — single-select or multi-select.

.. image:: /_static/examples/togglegroup-hero-light.png
   :class: bs-screenshot-light
   :alt: ToggleGroup — light theme

.. image:: /_static/examples/togglegroup-hero-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleGroup — dark theme

Usage
-----

Single select
~~~~~~~~~~~~~

In ``'single'`` mode (default) exactly one button is active at a time.

.. code-block:: python

   bs.ToggleGroup(["Day", "Week", "Month"], value="Week")

Multi select
~~~~~~~~~~~~

In ``'multi'`` mode any combination of buttons can be active. Pass the
initial selection as a ``set``.

.. code-block:: python

   bs.ToggleGroup(["Bold", "Italic", "Underline"],
                  mode="multi", value={"Bold", "Underline"})

Decoupled labels and the selected text
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Options accept ``(text, value)`` tuples or ``{"text": ..., "value": ...}`` dicts,
so a label can differ from its value. ``value`` is value-space; ``text`` mirrors
it as the selected label(s).

.. code-block:: python

   view = bs.ToggleGroup([("Grid view", "grid"), ("List view", "list")], value="grid")
   view.value      # -> "grid"        (single mode: the value)
   view.text       # -> "Grid view"   (single mode: the label)
   view.selection  # -> {"text": "Grid view", "value": "grid"}   (single: one record)

   tools = bs.ToggleGroup([("Bold", "b"), ("Italic", "i")], mode="multi", value={"b"})
   tools.value      # -> {"b"}          (multi mode: a set of values)
   tools.text       # -> {"Bold"}       (multi mode: a set of labels)
   tools.selection  # -> [{"text": "Bold", "value": "b"}]   (multi: list of records)

Options are a *data bag* — alongside the recognized keys (``text``, ``value``,
and the reserved ``icon``/``disabled``), any other key you add rides along and is
returned by ``.selection`` (see :doc:`select` for details).

.. image:: /_static/examples/togglegroup-multi-light.png
   :class: bs-screenshot-light
   :alt: ToggleGroup multi-select — light theme

.. image:: /_static/examples/togglegroup-multi-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleGroup multi-select — dark theme

Style variants
~~~~~~~~~~~~~~

Use ``variant=`` to control visual weight.

.. code-block:: python

   bs.ToggleGroup(["Off", "On"], accent="primary", variant="solid",   value="On")  # default
   bs.ToggleGroup(["Off", "On"], accent="primary", variant="outline", value="On")
   bs.ToggleGroup(["Off", "On"], accent="primary", variant="ghost",   value="On")

.. image:: /_static/examples/togglegroup-variants-light.png
   :class: bs-screenshot-light
   :alt: ToggleGroup style variants — light theme

.. image:: /_static/examples/togglegroup-variants-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleGroup style variants — dark theme

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.ToggleGroup(["Off", "On"], accent="primary",   value="On")
   bs.ToggleGroup(["Off", "On"], accent="secondary", value="On")
   bs.ToggleGroup(["Off", "On"], accent="info",      value="On")
   bs.ToggleGroup(["Off", "On"], accent="success",   value="On")
   bs.ToggleGroup(["Off", "On"], accent="warning",   value="On")
   bs.ToggleGroup(["Off", "On"], accent="danger",    value="On")

.. image:: /_static/examples/togglegroup-accents-light.png
   :class: bs-screenshot-light
   :alt: ToggleGroup accent colors — light theme

.. image:: /_static/examples/togglegroup-accents-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleGroup accent colors — dark theme

Orientation
~~~~~~~~~~~

.. code-block:: python

   bs.ToggleGroup(["Top", "Middle", "Bottom"], orient="horizontal")           # default
   bs.ToggleGroup(["Top", "Middle", "Bottom"], orient="vertical", value="Middle")

.. image:: /_static/examples/togglegroup-orientation-light.png
   :class: bs-screenshot-light
   :alt: ToggleGroup vertical orientation — light theme

.. image:: /_static/examples/togglegroup-orientation-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleGroup vertical orientation — dark theme

Reactive binding
~~~~~~~~~~~~~~~~

In single mode the signal holds a ``str``; in multi mode it holds a
``set[str]``. When ``signal=`` is provided, ``value=`` is ignored —
seed the Signal directly.

.. code-block:: python

   view = bs.Signal("grid")
   bs.ToggleGroup(["Grid", "List"], signal=view)
   view.subscribe(lambda v: set_layout(v))

   # Multi mode
   fmt = bs.Signal({"Bold"})
   bs.ToggleGroup(["Bold", "Italic", "Underline"], mode="multi", signal=fmt)

Disabled
~~~~~~~~

.. code-block:: python

   bs.ToggleGroup(["A", "B", "C"], value="B", disabled=True)
   bs.ToggleGroup(["X", "Y", "Z"], mode="multi", value={"X", "Z"}, disabled=True)

.. image:: /_static/examples/togglegroup-disabled-light.png
   :class: bs-screenshot-light
   :alt: ToggleGroup disabled — light theme

.. image:: /_static/examples/togglegroup-disabled-dark.png
   :class: bs-screenshot-dark
   :alt: ToggleGroup disabled — dark theme

Events
~~~~~~

.. code-block:: python

   group = bs.ToggleGroup(["Grid", "List"], value="Grid")

   group.on_change(lambda e: print("selected:", group.value))

   # As a Stream
   group.on_change().listen(lambda e: refresh(group.value))

Programmatic control
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   group = bs.ToggleGroup(["A", "B", "C"], value="A")

   group.value = "B"           # single mode — set by value
   group.value = {"A", "C"}    # multi mode — set by set
   group.disabled = True       # lock the group

   group.add("D")              # add an option at runtime
   group.remove("B")           # remove one
   group.configure_item("C", label="Charlie", disabled=True)  # relabel / disable one

   "D" in group                # membership test, by value
   len(group)                  # number of options

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

The complete reference for :class:`ToggleGroup <bootstack.ToggleGroup>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.ToggleGroup

Full Example
------------

.. literalinclude:: ../../docs/examples/togglegroup.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs