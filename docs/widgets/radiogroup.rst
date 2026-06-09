RadioGroup
==========

A group of mutually exclusive radio buttons.

.. image:: /_static/examples/radiogroup-hero-light.png
   :class: bs-screenshot-light
   :alt: RadioGroup — light theme

.. image:: /_static/examples/radiogroup-hero-dark.png
   :class: bs-screenshot-dark
   :alt: RadioGroup — dark theme

Usage
-----

Basic
~~~~~

Pass a list of strings — the label and value are the same for each option.

.. code-block:: python

   bs.RadioGroup(["Small", "Medium", "Large"], value="Medium")

Use ``(label, value)`` tuples when the display text should differ from the
stored value.

.. code-block:: python

   bs.RadioGroup([("Small", "s"), ("Medium", "m"), ("Large", "l")], value="m")

Orientation
~~~~~~~~~~~

.. code-block:: python

   bs.RadioGroup(["A", "B", "C"], orient="horizontal")  # default
   bs.RadioGroup(["A", "B", "C"], orient="vertical")

.. image:: /_static/examples/radiogroup-orientation-light.png
   :class: bs-screenshot-light
   :alt: RadioGroup orientation — light theme

.. image:: /_static/examples/radiogroup-orientation-dark.png
   :class: bs-screenshot-dark
   :alt: RadioGroup orientation — dark theme

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.RadioGroup(["Primary"],   accent="primary",   value="Primary")
   bs.RadioGroup(["Secondary"], accent="secondary", value="Secondary")
   bs.RadioGroup(["Info"],      accent="info",      value="Info")
   bs.RadioGroup(["Success"],   accent="success",   value="Success")
   bs.RadioGroup(["Warning"],   accent="warning",   value="Warning")
   bs.RadioGroup(["Danger"],    accent="danger",    value="Danger")

.. image:: /_static/examples/radiogroup-accents-light.png
   :class: bs-screenshot-light
   :alt: RadioGroup accent colors — light theme

.. image:: /_static/examples/radiogroup-accents-dark.png
   :class: bs-screenshot-dark
   :alt: RadioGroup accent colors — dark theme

Title
~~~~~

A ``title=`` adds a label rendered above the group.

.. code-block:: python

   bs.RadioGroup(
       [("Small", "s"), ("Medium", "m"), ("Large", "l")],
       title="Size", value="m",
   )
   bs.RadioGroup(
       [("Light", "light"), ("Dark", "dark"), ("Auto", "auto")],
       title="Theme", orient="vertical", value="auto",
   )

.. image:: /_static/examples/radiogroup-title-light.png
   :class: bs-screenshot-light
   :alt: RadioGroup title — light theme

.. image:: /_static/examples/radiogroup-title-dark.png
   :class: bs-screenshot-dark
   :alt: RadioGroup title — dark theme

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal`` with ``signal=``. The group and signal stay in sync.
When ``signal=`` is provided, ``value=`` is ignored — seed the Signal
directly.

.. code-block:: python

   size = bs.Signal("m")

   bs.RadioGroup([("Small", "s"), ("Medium", "m"), ("Large", "l")], signal=size)

   size.subscribe(lambda v: apply_size(v))

Runtime options
~~~~~~~~~~~~~~~

Add or remove options after construction.

.. code-block:: python

   group = bs.RadioGroup(["A", "B"])
   group.add("C")                        # label and value both "C"
   group.add("Delta", value="d")         # separate label and value
   group.remove("A")

Disabled
~~~~~~~~

.. code-block:: python

   bs.RadioGroup(["Alpha", "Beta", "Gamma"], value="Beta", disabled=True)

.. image:: /_static/examples/radiogroup-disabled-light.png
   :class: bs-screenshot-light
   :alt: RadioGroup disabled — light theme

.. image:: /_static/examples/radiogroup-disabled-dark.png
   :class: bs-screenshot-dark
   :alt: RadioGroup disabled — dark theme

Events
~~~~~~

.. code-block:: python

   group = bs.RadioGroup(["S", "M", "L"])

   # Fires whenever the selection changes
   group.on_change(lambda e: print("selected:", group.value))

   # As a Stream
   group.on_change().listen(lambda e: update_preview(group.value))

Programmatic control
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   group = bs.RadioGroup(["A", "B", "C"], value="A")

   group.value = "B"        # select programmatically
   group.disabled = True    # lock the group

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

The complete reference for :class:`RadioGroup <bootstack.RadioGroup>` lives on the
:doc:`bootstack </api-reference/bootstack>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.RadioGroup

Full Example
------------

.. literalinclude:: ../../docs/examples/radiogroup.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs