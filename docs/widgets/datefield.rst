DateField
=========

A date input field with locale-aware display formatting and an optional
calendar picker button. Supports single-date and date-range selection modes.

.. image:: /_static/examples/datefield-hero-light.png
   :class: bs-screenshot-light
   :alt: DateField — light theme

.. image:: /_static/examples/datefield-hero-dark.png
   :class: bs-screenshot-dark
   :alt: DateField — dark theme

A date field reads and writes a real ``date`` through
``field.value`` — ``None`` when empty, or a ``(start, end)`` tuple in range mode —
never a string. Users type a date or pick one from the calendar button;
``value_format`` controls only how it is displayed. Restrict what the picker
offers with ``min_date`` / ``max_date`` / ``disabled_dates``, and validate the
chosen date with rules.

Usage
-----

Basic usage
~~~~~~~~~~~

.. code-block:: python

   bs.DateField(label="Select a date")

Display formats
~~~~~~~~~~~~~~~

The ``value_format=`` parameter controls how dates are displayed in the field.
Any `ICU date format`_ pattern or named preset is accepted.

.. code-block:: python

   bs.DateField(value=today, value_format="longDate")     # January 15, 2025
   bs.DateField(value=today, value_format="shortDate")    # 1/15/25
   bs.DateField(value=today, value_format="monthAndYear") # January 2025

.. _ICU date format: https://unicode-org.github.io/icu/userguide/format_parse/datetime/

.. image:: /_static/examples/datefield-formats-light.png
   :class: bs-screenshot-light
   :alt: DateField formats — light theme

.. image:: /_static/examples/datefield-formats-dark.png
   :class: bs-screenshot-dark
   :alt: DateField formats — dark theme

Range mode
~~~~~~~~~~

Set ``selection_mode='range'`` to let the user pick a start and end date.
The entry becomes read-only in this mode — dates must be chosen via the picker.
``value`` returns a ``(start, end)`` tuple of ``date`` objects.

.. code-block:: python

   df = bs.DateField(
       selection_mode="range",
       range_start=date(2025, 1, 1),
       range_end=date(2025, 1, 31),
       label="Date range",
   )
   start, end = df.value  # tuple[date, date]

.. image:: /_static/examples/datefield-range-light.png
   :class: bs-screenshot-light
   :alt: DateField range mode — light theme

.. image:: /_static/examples/datefield-range-dark.png
   :class: bs-screenshot-dark
   :alt: DateField range mode — dark theme

Date constraints
~~~~~~~~~~~~~~~~

Use ``min_date=``, ``max_date=``, or ``disabled_dates=`` to restrict which
dates the picker shows as selectable.

.. code-block:: python

   from datetime import date, timedelta

   today = date.today()
   bs.DateField(
       label="Booking date",
       min_date=today,
       max_date=today + timedelta(days=30),
       disabled_dates=[today + timedelta(days=7)],
   )

``min_date``, ``max_date``, and ``disabled_dates`` are also live properties —
assign to them to update the constraints (the change takes effect the next time
the picker opens):

.. code-block:: python

   df.min_date = date.today()          # no past dates
   df.disabled_dates = booked_dates

Reactive binding
~~~~~~~~~~~~~~~~

Pass a ``Signal`` via ``signal=`` to two-way bind the field's ``date`` value to
application state. The signal carries the ``date`` object itself — not its text —
so reading it back gives you a ``date``. Seed it with a ``date`` to set the
initial value.

.. code-block:: python

   from datetime import date

   date_sig = bs.Signal(date.today())
   bs.DateField(label="Pick a date", signal=date_sig)

   # Derive a text signal for display
   date_text = date_sig.map(lambda d: d.strftime("%B %d, %Y") if d else "")
   bs.Label(textsignal=date_text, accent="secondary")

Handling changes
~~~~~~~~~~~~~~~~

``on_change()`` fires whenever the selected date changes — whether by keyboard
input, picker selection, or ``value=`` assignment.

.. code-block:: python

   df = bs.DateField(label="Appointment")
   df.on_change(lambda e: print("Selected:", e.value))

Validation
~~~~~~~~~~

Attach rules with ``add_validation_rule()``; they validate the field's **typed
value** — a ``date``, or ``None`` when empty. The ``range`` rule
checks date bounds with a message. This is distinct from ``min_date`` /
``max_date``, which restrict what the *picker* offers: a rule also catches an
out-of-range date the user **types**, and surfaces a message.

.. code-block:: python

   from datetime import date

   field = bs.DateField(label="Appointment")
   field.add_validation_rule(
       "range", max=date.today(),
       message="The date can't be in the future.",
       trigger="blur",
   )

   is_valid = field.validate()   # run every rule on demand

.. image:: /_static/examples/datefield-validation-light.png
   :class: bs-screenshot-light
   :alt: DateField validation — light theme

.. image:: /_static/examples/datefield-validation-dark.png
   :class: bs-screenshot-dark
   :alt: DateField validation — dark theme

Validity is reactive state. ``field.valid`` is a ``Signal[bool]`` and
``field.error`` a ``Signal[str]`` (the current message, ``""`` when valid) — bind
the error straight to a label and it keeps itself in sync:

.. code-block:: python

   bs.Label(textsignal=field.error, accent="danger")   # shows and clears itself

.. note::

   The full rule taxonomy, the ``range`` rule, and aggregating a whole form's
   validity live in the :doc:`Validation </reference/validation>` guide.

States
~~~~~~

.. code-block:: python

   bs.DateField(value=today, label="Normal")
   bs.DateField(value=today, label="Read only", read_only=True)
   bs.DateField(value=today, label="Disabled",  disabled=True)

.. image:: /_static/examples/datefield-states-light.png
   :class: bs-screenshot-light
   :alt: DateField states — light theme

.. image:: /_static/examples/datefield-states-dark.png
   :class: bs-screenshot-dark
   :alt: DateField states — dark theme

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`timefield` — time input with clock picker
* :doc:`textfield` — plain single-line text input
* :doc:`Validation </reference/validation>` — the full rule set and form-level validity
* :doc:`Composing Fields </tasks/composing-fields>` — add buttons or icons inside a field
* :doc:`Signals </reference/signals>` — reactive binding for fields

API
---

The complete reference for :class:`DateField <bootstack.DateField>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.DateField

Full Example
------------

.. literalinclude:: ../../docs/examples/datefield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs