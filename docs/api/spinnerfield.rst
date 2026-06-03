SpinnerField
============

A text-entry field with up/down spin buttons for stepping through a fixed list
of values or a numeric range.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/spinnerfield-hero-light.png"
        alt="SpinnerField — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/spinnerfield-hero-dark.png"
        alt="SpinnerField — dark theme" style="max-width:100%;">

Usage
-----

Text mode
~~~~~~~~~

Pass ``options=`` to step through a fixed list of strings. The spin buttons
cycle forward and back through the list.

.. code-block:: python

   bs.SpinnerField(
       label="Priority",
       options=["Low", "Medium", "High", "Critical"],
       value="Medium",
   )

Numeric mode
~~~~~~~~~~~~

Use ``min_value=``, ``max_value=``, and ``step=`` instead of ``options=``
for a numeric range. Only one mode should be used at a time.

.. code-block:: python

   bs.SpinnerField(
       label="Quantity",
       value=1,
       min_value=1,
       max_value=99,
       step=1,
   )

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/spinnerfield-modes-light.png"
        alt="SpinnerField modes — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/spinnerfield-modes-dark.png"
        alt="SpinnerField modes — dark theme" style="max-width:100%;">

Wrap around
~~~~~~~~~~~

Set ``wrap=True`` to cycle back to the start when the end of the list (or
range) is reached, and vice versa.

.. code-block:: python

   bs.SpinnerField(
       label="Month",
       options=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
       value="Jan",
       wrap=True,
   )

Label and message
~~~~~~~~~~~~~~~~~

Use ``label=`` for a field title and ``message=`` for helper text below.

.. code-block:: python

   bs.SpinnerField(
       label="Font size",
       value=12,
       min_value=6,
       max_value=72,
       step=2,
       message="Applies to the selected text.",
   )

States
~~~~~~

.. code-block:: python

   bs.SpinnerField(value=5, min_value=1, max_value=10, label="Normal")
   bs.SpinnerField(value=5, min_value=1, max_value=10, label="Read only", read_only=True)
   bs.SpinnerField(value=5, min_value=1, max_value=10, label="Disabled",  disabled=True)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/spinnerfield-states-light.png"
        alt="SpinnerField states — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/spinnerfield-states-dark.png"
        alt="SpinnerField states — dark theme" style="max-width:100%;">

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal[str]`` with ``textsignal=``. The field and signal stay in
sync automatically.

.. code-block:: python

   size = bs.Signal("M")
   bs.SpinnerField(
       label="T-shirt size",
       options=["XS", "S", "M", "L", "XL", "XXL"],
       textsignal=size,
   )
   bs.Label(textsignal=size, accent="secondary")

Handling changes
~~~~~~~~~~~~~~~~

Use ``on_change()`` to respond when the value changes — whether from a spin
button click, keyboard arrow key, or direct text entry.

.. code-block:: python

   sf = bs.SpinnerField(
       label="Rating",
       options=["★", "★★", "★★★", "★★★★", "★★★★★"],
       value="★★★",
       wrap=True,
   )

   def handle_change(e):
       print("Selected:", sf.value)

   sf.on_change(handle_change)

   # As a subscription (cancellable)
   sub = sf.on_change(handle_change)
   sub.cancel()

   # As a Stream (composable)
   sf.on_change().listen(handle_change)

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`numberfield` — numeric-only input with stepper buttons
* :doc:`select` — dropdown picker for longer lists

API
---

.. autoclass:: bootstack.widgets.spinnerfield.SpinnerField
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: tk

Full Example
------------

.. literalinclude:: ../../docs/examples/spinnerfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs