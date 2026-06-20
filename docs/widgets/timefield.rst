TimeField
=========

A time input field with a searchable dropdown list of time intervals. The user
can type a custom time or select from the dropdown.

.. image:: /_static/examples/timefield-hero-light.png
   :class: bs-screenshot-light
   :alt: TimeField — light theme

.. image:: /_static/examples/timefield-hero-dark.png
   :class: bs-screenshot-dark
   :alt: TimeField — dark theme

A time field reads and writes a real ``time`` through ``field.value`` — or
``None`` when empty. The user types a time (``'14:30'`` or ``'2:30 PM'``) or picks
one from the dropdown; ``value_format`` controls only how it is displayed, and
``min_time`` / ``max_time`` limit which times the dropdown offers. The field
starts empty — pass ``value=`` to seed a starting time.

Usage
-----

Basic usage
~~~~~~~~~~~

.. code-block:: python

   bs.TimeField(label="Select a time")

Display formats
~~~~~~~~~~~~~~~

The ``value_format=`` parameter controls how times are displayed in the field.
Any `ICU time format`_ pattern or named preset is accepted.

.. code-block:: python

   now = datetime.time(14, 30)
   bs.TimeField(value=now, value_format="shortTime")   # 2:30 PM
   bs.TimeField(value=now, value_format="HH:mm")       # 14:30
   bs.TimeField(value=now, value_format="HH:mm:ss")    # 14:30:00

.. _ICU time format: https://unicode-org.github.io/icu/userguide/format_parse/datetime/

.. image:: /_static/examples/timefield-formats-light.png
   :class: bs-screenshot-light
   :alt: TimeField formats — light theme

.. image:: /_static/examples/timefield-formats-dark.png
   :class: bs-screenshot-dark
   :alt: TimeField formats — dark theme

Dropdown interval
~~~~~~~~~~~~~~~~~

The ``interval=`` parameter sets the spacing between entries in the dropdown.

.. code-block:: python

   bs.TimeField(interval=15)   # every 15 minutes
   bs.TimeField(interval=30)   # every 30 minutes (default)
   bs.TimeField(interval=60)   # hourly

.. image:: /_static/examples/timefield-intervals-light.png
   :class: bs-screenshot-light
   :alt: TimeField intervals — light theme

.. image:: /_static/examples/timefield-intervals-dark.png
   :class: bs-screenshot-dark
   :alt: TimeField intervals — dark theme

Time range constraints
~~~~~~~~~~~~~~~~~~~~~~

Use ``min_time=`` and ``max_time=`` to limit which times appear in the dropdown.

.. code-block:: python

   import datetime

   bs.TimeField(
       label="Appointment time",
       message="Available 9 AM – 5 PM.",
       min_time=datetime.time(9, 0),
       max_time=datetime.time(17, 0),
       interval=30,
   )

Reactive binding
~~~~~~~~~~~~~~~~

Pass a ``Signal`` via ``signal=`` to two-way bind the field's ``time`` value to
application state. The signal carries the ``time`` object itself — not its text —
so reading it back gives you a ``time``. Seed it with a ``time`` to set the
initial value.

.. code-block:: python

   from datetime import time

   time_sig = bs.Signal(time(9, 0))
   bs.TimeField(label="Pick a time", signal=time_sig)

   # Derive a text signal for display
   time_text = time_sig.map(lambda t: t.strftime("%I:%M %p") if t else "")
   bs.Label(textsignal=time_text, accent="secondary")

Handling changes
~~~~~~~~~~~~~~~~

``on_change()`` fires whenever the time value changes — whether by typing,
dropdown selection, or ``value=`` assignment.

.. code-block:: python

   tf = bs.TimeField(label="Start time")
   tf.on_change(lambda e: print("Selected:", e.value))

Validation
~~~~~~~~~~

Attach rules with ``add_validation_rule()``; they validate the field's **typed
value** — a ``time``, or ``None`` when empty. The ``range`` rule checks time
bounds with a message. This is distinct from ``min_time`` / ``max_time``, which
limit the *dropdown*: a rule also catches an out-of-range time the user **types**,
and surfaces a message.

.. code-block:: python

   import datetime

   field = bs.TimeField(label="Appointment")
   field.add_validation_rule(
       "range",
       min=datetime.time(9, 0), max=datetime.time(17, 0),
       message="Choose a time between 9 AM and 5 PM.",
       trigger="blur",
   )

   is_valid = field.validate()   # run every rule on demand

.. image:: /_static/examples/timefield-validation-light.png
   :class: bs-screenshot-light
   :alt: TimeField validation — light theme

.. image:: /_static/examples/timefield-validation-dark.png
   :class: bs-screenshot-dark
   :alt: TimeField validation — dark theme

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

   bs.TimeField(value=now, label="Normal")
   bs.TimeField(value=now, label="Read only", read_only=True)
   bs.TimeField(value=now, label="Disabled",  disabled=True)

.. image:: /_static/examples/timefield-states-light.png
   :class: bs-screenshot-light
   :alt: TimeField states — light theme

.. image:: /_static/examples/timefield-states-dark.png
   :class: bs-screenshot-dark
   :alt: TimeField states — dark theme

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`datefield` — date input with calendar picker
* :doc:`textfield` — plain single-line text input
* :doc:`Validation </reference/validation>` — the full rule set and form-level validity
* :doc:`Composing Fields </tasks/composing-fields>` — add buttons or icons inside a field
* :doc:`Signals </reference/signals>` — reactive binding for fields

API
---

The complete reference for :class:`TimeField <bootstack.TimeField>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.TimeField

Full Example
------------

.. literalinclude:: ../../docs/examples/timefield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs