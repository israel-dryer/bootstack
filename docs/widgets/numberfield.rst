NumberField
===========

Numeric input with optional stepper buttons, bounds enforcement, and keyboard/
mouse-wheel stepping.

.. image:: /_static/examples/numberfield-hero-light.png
   :class: bs-screenshot-light
   :alt: NumberField demo — light theme

.. image:: /_static/examples/numberfield-hero-dark.png
   :class: bs-screenshot-dark
   :alt: NumberField demo — dark theme

A number field reads and writes a real ``int`` or ``float`` through
``field.value`` — or ``None`` when empty — never a string. Bind a
:doc:`Signal </reference/signals>` with ``signal=`` to keep a typed variable in
lockstep. Type into it, press the ±steppers, or step with the arrow keys and
mouse wheel; ``min_value``/``max_value`` clamp the result, while ``value_format``
changes only how the number is displayed.

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
automatically at the bounds. Set ``wrap=True`` to wrap from the maximum back to
the minimum (and vice versa) when stepping past a bound.

.. code-block:: python

   bs.NumberField(min_value=0,   max_value=100, step=5,   label="0–100, step 5")
   bs.NumberField(min_value=0.0, max_value=1.0, step=0.1, label="0.0–1.0, step 0.1")
   bs.NumberField(min_value=1, max_value=12, value=12, wrap=True, label="Month (wraps)")

Stepper buttons
~~~~~~~~~~~~~~~

The +/− buttons are shown by default. Hide them with ``show_steppers=False``.

.. code-block:: python

   bs.NumberField(label="With steppers", value=25)
   bs.NumberField(label="No steppers",   value=25, show_steppers=False)

.. image:: /_static/examples/numberfield-steppers-light.png
   :class: bs-screenshot-light
   :alt: NumberField stepper buttons — light theme

.. image:: /_static/examples/numberfield-steppers-dark.png
   :class: bs-screenshot-dark
   :alt: NumberField stepper buttons — dark theme

Programmatic stepping
~~~~~~~~~~~~~~~~~~~~~

Call ``increment()`` and ``decrement()`` to step the value in code.

.. code-block:: python

   field = bs.NumberField(value=10, step=5)
   field.increment()    # → 15
   field.decrement(2)   # → 5
   field.clear()        # empties the field — value becomes None, not 0

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

.. image:: /_static/examples/numberfield-value-format-light.png
   :class: bs-screenshot-light
   :alt: NumberField value formatting — light theme

.. image:: /_static/examples/numberfield-value-format-dark.png
   :class: bs-screenshot-dark
   :alt: NumberField value formatting — dark theme

States
~~~~~~

.. code-block:: python

   bs.NumberField(value=42, label="Normal")
   bs.NumberField(value=42, label="Read only", read_only=True)
   bs.NumberField(value=42, label="Disabled",  disabled=True)

.. image:: /_static/examples/numberfield-states-light.png
   :class: bs-screenshot-light
   :alt: NumberField states — light theme

.. image:: /_static/examples/numberfield-states-dark.png
   :class: bs-screenshot-dark
   :alt: NumberField states — dark theme

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal`` with ``signal=`` to keep a typed numeric variable and the field
in sync. The signal carries the parsed ``int``/``float``, not the text — use a
float-typed ``Signal(0.0)`` when the field accepts decimals.

.. code-block:: python

   qty = bs.Signal(1)                       # int-typed; Signal(0.0) for decimals
   field = bs.NumberField(label="Quantity", signal=qty, min_value=1)
   qty.set(5)            # updates the field
   field.value          # 5  (a number, never a string)

A number field binds its numeric value, so ``signal=`` is the only binding it
takes — pass a number-typed ``Signal``, never a string.

Validation
~~~~~~~~~~

Attach rules with ``add_validation_rule()``; they validate the field's **typed
value** — a number, or ``None`` when empty. The ``range`` rule checks numeric
bounds with a message (distinct from the silent clamping of ``min_value`` /
``max_value``):

.. code-block:: python

   field = bs.NumberField(label="Age")
   field.add_validation_rule(
       "range", min=0, max=120,
       message="Age must be between 0 and 120.",
       trigger="blur",
   )

   is_valid = field.validate()   # run every rule on demand

.. image:: /_static/examples/numberfield-validation-light.png
   :class: bs-screenshot-light
   :alt: NumberField validation — light theme

.. image:: /_static/examples/numberfield-validation-dark.png
   :class: bs-screenshot-dark
   :alt: NumberField validation — dark theme

Validity is reactive state. ``field.valid`` is a ``Signal[bool]`` and
``field.error`` a ``Signal[str]`` (the current message, ``""`` when valid) — bind
the error straight to a label and it keeps itself in sync:

.. code-block:: python

   bs.Label(textsignal=field.error, accent="danger")   # shows and clears itself

.. note::

   The full rule taxonomy, the ``range`` rule, ``custom`` rules (whose ``func``
   receives the typed number, not text), and aggregating a whole form's validity
   live in the :doc:`Validation </reference/validation>` guide.

Keyboard
~~~~~~~~

- **Up / Down** — step the value by ``step`` (commits like a stepper press).
- **Mouse wheel** — step up or down while the field is focused.
- **Enter** — commit the current input and fire ``on_submit``.

Stepping past a bound clamps to it, or wraps to the opposite bound when
``wrap=True``. Stepping does nothing while the field is read-only or disabled.

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`textfield` — plain text input
* :doc:`slider` — drag-to-set numeric value
* :doc:`Validation </reference/validation>` — the full rule set, typed-value model, and form validity
* :doc:`Composing Fields </tasks/composing-fields>` — add buttons or icons inside a field, and reusable field types
* :doc:`Signals </reference/signals>` — the reactive binding behind ``signal=``

API
---

The complete reference for :class:`NumberField <bootstack.NumberField>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.NumberField

Full Example
------------

.. literalinclude:: ../../docs/examples/numberfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
