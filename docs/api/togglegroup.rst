ToggleGroup
===========

A group of toggle buttons — single-select or multi-select.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/togglegroup-light.png"
        alt="ToggleGroup demo — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/togglegroup-dark.png"
        alt="ToggleGroup demo — dark theme"
        style="max-width:100%;">

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

Style variants
~~~~~~~~~~~~~~

Use ``variant=`` to control visual weight.

.. code-block:: python

   bs.ToggleGroup(["A", "B", "C"], variant="solid",   value="A")  # default
   bs.ToggleGroup(["A", "B", "C"], variant="outline",  value="A")
   bs.ToggleGroup(["A", "B", "C"], variant="ghost",    value="A")

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.ToggleGroup(["A", "B"], accent="primary",  value="A")
   bs.ToggleGroup(["A", "B"], accent="success",  value="A")
   bs.ToggleGroup(["A", "B"], accent="danger",   value="A")

Orientation
~~~~~~~~~~~

.. code-block:: python

   bs.ToggleGroup(["A", "B", "C"], orient="horizontal")  # default
   bs.ToggleGroup(["A", "B", "C"], orient="vertical",    value="A")

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

   group.value = "B"       # single mode — set by value
   group.value = {"A", "C"}  # multi mode — set by set
   group.disabled = True   # lock the group

   group.add("D")          # add option at runtime

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

.. autoclass:: bootstack.widgets.togglegroup.ToggleGroup
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/togglegroup.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
