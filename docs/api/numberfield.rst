NumberField
===========

Numeric input with optional stepper buttons, bounds enforcement, and keyboard/
mouse-wheel stepping.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/numberfield-hero-light.png"
        alt="NumberField demo — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/numberfield-hero-dark.png"
        alt="NumberField demo — dark theme"
        style="max-width:100%;">

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

Use ``label=`` for a field title and ``message=`` for helper text below.

.. code-block:: python

   bs.NumberField(
       label="Quantity",
       message="Enter a value between 0 and 100.",
   )

Required
~~~~~~~~

Set ``required=True`` to mark the field visually and prevent empty submission.

.. code-block:: python

   bs.NumberField(label="Quantity", required=True)

Bounds and step
~~~~~~~~~~~~~~~

Use ``min_value=``, ``max_value=``, and ``step=`` to constrain input.
Arrow keys and the mouse wheel step by ``step``. Stepper buttons disable
automatically at the bounds.

.. code-block:: python

   bs.NumberField(min_value=0,   max_value=100, step=5,   label="0–100, step 5")
   bs.NumberField(min_value=0.0, max_value=1.0, step=0.1, label="0.0–1.0, step 0.1")

Stepper buttons
~~~~~~~~~~~~~~~

The +/− buttons are shown by default. Hide them with ``show_steppers=False``.

.. code-block:: python

   bs.NumberField(label="With steppers", value=25)
   bs.NumberField(label="No steppers",   value=25, show_steppers=False)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/numberfield-steppers-light.png"
        alt="NumberField stepper buttons — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/numberfield-steppers-dark.png"
        alt="NumberField stepper buttons — dark theme"
        style="max-width:100%;">

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
Requires localization to be enabled.

.. code-block:: python

   bs.NumberField(1234567, value_format="#,##0",    label="Thousands",  show_steppers=False)
   bs.NumberField(3.14159, value_format="#,##0.00", label="2 decimals", show_steppers=False)
   bs.NumberField(0.75,    value_format="percent",  label="Percent",    show_steppers=False)
   bs.NumberField(9.99,    value_format="currency", label="Currency",   show_steppers=False)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/numberfield-value-format-light.png"
        alt="NumberField value formatting — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/numberfield-value-format-dark.png"
        alt="NumberField value formatting — dark theme"
        style="max-width:100%;">

States
~~~~~~

.. code-block:: python

   bs.NumberField(value=42, label="Normal")
   bs.NumberField(value=42, label="Read only", read_only=True)
   bs.NumberField(value=42, label="Disabled",  disabled=True)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/numberfield-states-light.png"
        alt="NumberField states — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/numberfield-states-dark.png"
        alt="NumberField states — dark theme"
        style="max-width:100%;">

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal`` with ``textsignal=``. The field and signal stay in sync
automatically. Initialize the signal with a string value, not a number.

.. code-block:: python

   qty = bs.Signal("1")
   bs.NumberField(label="Quantity", textsignal=qty, min_value=1)
   bs.Label(textsignal=qty, accent="secondary")

Validation
~~~~~~~~~~

Attach rules with ``add_validation_rule()``. Rules run on the configured
trigger (``'blur'``, ``'key'``, or ``'manual'``).

.. code-block:: python

   field = bs.NumberField(label="Age")
   field.add_validation_rule(
       "custom",
       func=lambda v: v != "" and 0 <= float(v) <= 120,
       message="Age must be between 0 and 120.",
       trigger="blur",
   )

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/numberfield-validation-light.png"
        alt="NumberField validation — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/numberfield-validation-dark.png"
        alt="NumberField validation — dark theme"
        style="max-width:100%;">

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`textfield` — plain text input
* :doc:`passwordfield` — masked password input
* :doc:`slider` — drag-to-set numeric value

API
---

.. autoclass:: bootstack.widgets.numberfield.NumberField
   :members:
   :undoc-members:
   :inherited-members: FieldAddonMixin
   :exclude-members: tk

Full Example
------------

.. literalinclude:: ../../docs/examples/numberfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
