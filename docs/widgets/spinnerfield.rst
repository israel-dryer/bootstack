SpinnerField
============

A text-entry field with up/down spin buttons for stepping through a fixed list
of values or a numeric range.

.. image:: /_static/examples/spinnerfield-hero-light.png
   :class: bs-screenshot-light
   :alt: SpinnerField — light theme

.. image:: /_static/examples/spinnerfield-hero-dark.png
   :class: bs-screenshot-dark
   :alt: SpinnerField — dark theme

Usage
-----

A spinner steps with the up/down buttons or the arrow keys, in one of two modes:
pass ``options=`` to cycle a list of strings, or ``min_value`` / ``max_value`` /
``step`` for a numeric range — not both. ``field.value`` is the current string
(text mode) or number (numeric mode), and ``textsignal=`` binds the displayed
text. For free numeric entry without a fixed step reach for
:doc:`NumberField <numberfield>`; for a long list, :doc:`Select <select>`.

Text mode
~~~~~~~~~

Pass ``options=`` to step through a fixed list of strings. The spin buttons
cycle forward and back through the list.

.. code-block:: python

   bs.SpinnerField(
       label="Text mode",
       options=["Small", "Medium", "Large", "X-Large"],
       value="Medium",
   )

Numeric mode
~~~~~~~~~~~~

Use ``min_value=``, ``max_value=``, and ``step=`` instead of ``options=``
for a numeric range. Only one mode should be used at a time.

.. code-block:: python

   bs.SpinnerField(
       label="Numeric mode",
       value=10,
       min_value=0,
       max_value=100,
       step=5,
   )

.. image:: /_static/examples/spinnerfield-modes-light.png
   :class: bs-screenshot-light
   :alt: SpinnerField modes — light theme

.. image:: /_static/examples/spinnerfield-modes-dark.png
   :class: bs-screenshot-dark
   :alt: SpinnerField modes — dark theme

Value formatting
~~~~~~~~~~~~~~~~

In numeric mode, ``value_format=`` displays the value with a locale-aware ICU
pattern — the raw number is preserved internally; only the display changes.
Requires localization to be enabled.

.. code-block:: python

   bs.SpinnerField(label="Price", value=10, min_value=0, max_value=100,
                   value_format="currency")

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

.. image:: /_static/examples/spinnerfield-states-light.png
   :class: bs-screenshot-light
   :alt: SpinnerField states — light theme

.. image:: /_static/examples/spinnerfield-states-dark.png
   :class: bs-screenshot-dark
   :alt: SpinnerField states — dark theme

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

Validation
~~~~~~~~~~

A spinner constrains its own values — the list, or the numeric range — so
validation is usually just ``required`` for a mandatory choice. Attach rules with
``add_validation_rule()``; they run against the field's text value.

.. code-block:: python

   field = bs.SpinnerField(label="Size", options=["S", "M", "L"], required=True)

Validity is reactive state — ``field.valid`` is a ``Signal[bool]`` and
``field.error`` a ``Signal[str]`` (``""`` when valid). Bind the error to a label
to surface it:

.. code-block:: python

   bs.Label(textsignal=field.error, accent="danger")   # shows and clears itself

.. note::

   The full rule taxonomy and aggregating a whole form's validity live in the
   :doc:`Validation </reference/validation>` guide.

Programmatic stepping
~~~~~~~~~~~~~~~~~~~~~

Call ``increment()`` and ``decrement()`` to step the value in code — the same
as pressing the spin buttons. They work in both modes and honor the field's
bounds and ``wrap`` setting.

.. code-block:: python

   field = bs.SpinnerField(value=10, min_value=0, max_value=100, step=5)
   field.increment()    # → 15
   field.decrement(2)   # → 5

   picker = bs.SpinnerField(value="Low", options=["Low", "Medium", "High"])
   picker.increment()   # → "Medium"

Keyboard
~~~~~~~~

- **Up / Down** — step to the next or previous value (the same as the spin
  buttons).
- **Mouse wheel** — step while the field is focused.

Stepping stops at the first and last value, or wraps around when ``wrap=True``.
It does nothing while the field is read-only or disabled.

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`numberfield` — numeric-only input with stepper buttons
* :doc:`select` — dropdown picker for longer lists
* :doc:`Validation </reference/validation>` — the full rule set and form-level validity
* :doc:`Signals </reference/signals>` — the reactive binding behind ``textsignal=``

API
---

The complete reference for :class:`SpinnerField <bootstack.SpinnerField>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.SpinnerField

Full Example
------------

.. literalinclude:: ../../docs/examples/spinnerfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs