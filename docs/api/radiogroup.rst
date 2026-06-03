RadioGroup
==========

A group of mutually exclusive radio buttons.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/radiogroup-hero-light.png"
        alt="RadioGroup — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/radiogroup-hero-dark.png"
        alt="RadioGroup — dark theme"
        style="max-width:100%;">

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

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/radiogroup-orientation-light.png"
        alt="RadioGroup orientation — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/radiogroup-orientation-dark.png"
        alt="RadioGroup orientation — dark theme"
        style="max-width:100%;">

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.RadioGroup(["Primary"],   accent="primary",   value="Primary")
   bs.RadioGroup(["Secondary"], accent="secondary", value="Secondary")
   bs.RadioGroup(["Info"],      accent="info",      value="Info")
   bs.RadioGroup(["Success"],   accent="success",   value="Success")
   bs.RadioGroup(["Warning"],   accent="warning",   value="Warning")
   bs.RadioGroup(["Danger"],    accent="danger",    value="Danger")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/radiogroup-accents-light.png"
        alt="RadioGroup accent colors — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/radiogroup-accents-dark.png"
        alt="RadioGroup accent colors — dark theme"
        style="max-width:100%;">

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

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/radiogroup-title-light.png"
        alt="RadioGroup title — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/radiogroup-title-dark.png"
        alt="RadioGroup title — dark theme"
        style="max-width:100%;">

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

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/radiogroup-disabled-light.png"
        alt="RadioGroup disabled — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/radiogroup-disabled-dark.png"
        alt="RadioGroup disabled — dark theme"
        style="max-width:100%;">

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

.. autoclass:: bootstack.widgets.radiogroup.RadioGroup
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/radiogroup.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs