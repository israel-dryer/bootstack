NumberField
===========

Numeric input with optional stepper buttons, bounds enforcement, and keyboard/
mouse-wheel stepping.

.. code-block:: python

   bs.NumberField(label="Quantity", min_value=0, max_value=100)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/numberfield-light.png"
        alt="NumberField demo — light theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/numberfield-dark.png"
        alt="NumberField demo — dark theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">

Usage
-----

Basic
~~~~~

.. code-block:: python

   bs.NumberField()
   bs.NumberField(42)
   bs.NumberField(3.14, step=0.01)

Label and message
~~~~~~~~~~~~~~~~~

.. code-block:: python

   bs.NumberField(
       label="Quantity",
       message="Enter a value between 0 and 100.",
   )

Bounds and step
~~~~~~~~~~~~~~~

Use ``min_value=``, ``max_value=``, and ``step=`` to constrain input.
Arrow keys and the mouse wheel step by ``step``.

.. code-block:: python

   bs.NumberField(min_value=0, max_value=100, step=5)
   bs.NumberField(min_value=0.0, max_value=1.0, step=0.1)

Stepper buttons
~~~~~~~~~~~~~~~

The +/− buttons are shown by default. Hide them with
``show_steppers=False``.

.. code-block:: python

   bs.NumberField(label="With steppers")
   bs.NumberField(label="No steppers", show_steppers=False)

Programmatic stepping
~~~~~~~~~~~~~~~~~~~~~

Call ``increment()`` and ``decrement()`` to step the value in code.

.. code-block:: python

   field = bs.NumberField(value=10, step=5)
   field.increment()    # → 15
   field.decrement(2)   # → 5

Value formatting
~~~~~~~~~~~~~~~~

Use ``value_format=`` to display the number with a locale-aware ICU pattern.
The raw numeric value is preserved internally; only the display changes.

.. code-block:: python

   bs.NumberField(1234567, value_format="#,##0",    label="Thousands")
   bs.NumberField(3.14159, value_format="#,##0.00", label="2 decimals")
   bs.NumberField(0.75,    value_format="percent",  label="Percent")
   bs.NumberField(9.99,    value_format="currency", label="Currency")

States
~~~~~~

.. code-block:: python

   bs.NumberField(value=42, label="Normal")
   bs.NumberField(value=42, label="Read only", read_only=True)
   bs.NumberField(value=42, label="Disabled",  disabled=True)

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal`` with ``textsignal=``. The field and signal stay in sync.

.. code-block:: python

   qty = bs.Signal(1)
   bs.NumberField(label="Quantity", textsignal=qty, min_value=1)
   bs.Label(textsignal=qty, accent="secondary")

Validation
~~~~~~~~~~

.. code-block:: python

   from bootstack.validation import ValidationRule

   field = bs.NumberField(label="Age")
   field.add_validation_rule(ValidationRule(
       "custom",
       func=lambda v: 0 <= float(v) <= 120,
       message="Age must be between 0 and 120.",
       trigger="blur",
   ))

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

.. autoclass:: bootstack.widgets.numberfield.NumberField
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/numberfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
