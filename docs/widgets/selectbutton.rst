SelectButton
============

A button that opens a dropdown value list and displays the current selection.

.. image:: /_static/examples/selectbutton-hero-light.png
   :class: bs-screenshot-light
   :alt: SelectButton — light theme

.. image:: /_static/examples/selectbutton-hero-dark.png
   :class: bs-screenshot-dark
   :alt: SelectButton — dark theme

Usage
-----

Basic
~~~~~

Pass a list of options. The button displays the currently selected value.

.. code-block:: python

   bs.SelectButton(["Light", "Dark", "Auto"], value="Light")

Option values
~~~~~~~~~~~~~

Like `Select`, an option's label can differ from its value — pass a
``(text, value)`` tuple or a ``{"text": ..., "value": ...}`` dict. ``value=``,
``.value``, and the change event are in value-space.

.. code-block:: python

   mode = bs.SelectButton([("Light theme", "light"), ("Dark theme", "dark")], value="dark")
   mode.value             # -> "dark"          (the value)
   mode.text              # -> "Dark theme"    (the displayed label)
   mode.selection         # -> {"text": "Dark theme", "value": "dark"}   (the full record)
   mode.on_change(lambda e: apply_theme(e.value))

Options are a *data bag* — alongside the recognized keys (``text``, ``value``,
and the per-option ``icon``/``disabled``), any other key you add rides along and is
returned by ``.selection`` (see :doc:`select` for details). A per-option ``icon``
renders beside that menu item's label, and ``disabled`` greys out a single option
so it can't be chosen — distinct from the widget-level ``disabled=`` that locks
the whole control.

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.SelectButton(["Primary"],   accent="primary",   value="Primary")
   bs.SelectButton(["Secondary"], accent="secondary", value="Secondary")
   bs.SelectButton(["Info"],      accent="info",      value="Info")
   bs.SelectButton(["Success"],   accent="success",   value="Success")
   bs.SelectButton(["Warning"],   accent="warning",   value="Warning")
   bs.SelectButton(["Danger"],    accent="danger",    value="Danger")

.. image:: /_static/examples/selectbutton-accents-light.png
   :class: bs-screenshot-light
   :alt: SelectButton accent colors — light theme

.. image:: /_static/examples/selectbutton-accents-dark.png
   :class: bs-screenshot-dark
   :alt: SelectButton accent colors — dark theme

Style variants
~~~~~~~~~~~~~~

.. code-block:: python

   bs.SelectButton(["Solid"],   accent="primary", variant="solid")
   bs.SelectButton(["Outline"], accent="primary", variant="outline")
   bs.SelectButton(["Ghost"],   accent="primary", variant="ghost")

.. image:: /_static/examples/selectbutton-variants-light.png
   :class: bs-screenshot-light
   :alt: SelectButton style variants — light theme

.. image:: /_static/examples/selectbutton-variants-dark.png
   :class: bs-screenshot-dark
   :alt: SelectButton style variants — dark theme

With icon
~~~~~~~~~

.. code-block:: python

   bs.SelectButton(["Light", "Dark", "Auto"],
                   value="Dark", icon="moon-fill")
   bs.SelectButton(["Small", "Medium", "Large"],
                   value="Large", icon="fonts", accent="secondary")

.. image:: /_static/examples/selectbutton-icon-light.png
   :class: bs-screenshot-light
   :alt: SelectButton with icon — light theme

.. image:: /_static/examples/selectbutton-icon-dark.png
   :class: bs-screenshot-dark
   :alt: SelectButton with icon — dark theme

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal[str]`` with ``signal=``. The button and signal stay in
sync. When ``signal=`` is provided, ``value=`` is ignored — seed the
Signal directly.

.. code-block:: python

   theme = bs.Signal("light")
   bs.SelectButton(["Light", "Dark", "Auto"], signal=theme)
   theme.subscribe(lambda v: bs.set_theme(v.lower()))

Disabled
~~~~~~~~

.. code-block:: python

   bs.SelectButton(["A", "B", "C"], value="B", disabled=True)
   bs.SelectButton(["A", "B", "C"], value="B", disabled=True,
                   accent="primary", variant="outline")

.. image:: /_static/examples/selectbutton-disabled-light.png
   :class: bs-screenshot-light
   :alt: SelectButton disabled — light theme

.. image:: /_static/examples/selectbutton-disabled-dark.png
   :class: bs-screenshot-dark
   :alt: SelectButton disabled — dark theme

Events
~~~~~~

.. code-block:: python

   btn = bs.SelectButton(["Small", "Medium", "Large"], value="Medium")

   btn.on_change(lambda e: print("selected:", btn.value))

   # As a Stream
   btn.on_change().listen(lambda e: apply_size(btn.value))

Programmatic control
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   btn = bs.SelectButton(["A", "B", "C"], value="A")

   btn.value = "C"                 # change selection
   btn.disabled = True             # lock the button
   btn.options = ["X", "Y", "Z"]   # replace the choice list (rebuilds the dropdown)

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

The complete reference for :class:`SelectButton <bootstack.SelectButton>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.SelectButton

Full Example
------------

.. literalinclude:: ../../docs/examples/selectbutton.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs