RadioGroup
==========

A group of mutually exclusive radio buttons.

.. code-block:: python

   bs.RadioGroup(["Small", "Medium", "Large"], value="Medium")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/radiogroup-light.png"
        alt="RadioGroup demo — light theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/radiogroup-dark.png"
        alt="RadioGroup demo — dark theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">

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

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.RadioGroup(["Off", "On"], accent="primary", value="On")
   bs.RadioGroup(["Off", "On"], accent="success", value="On")
   bs.RadioGroup(["Off", "On"], accent="danger",  value="On")

Title
~~~~~

A ``title=`` adds a label rendered above the group.

.. code-block:: python

   bs.RadioGroup(
       [("Small", "s"), ("Medium", "m"), ("Large", "l")],
       title="Size",
       value="m",
   )

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
