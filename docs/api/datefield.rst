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
   bs.DateField(value=today, value_format="yyyy-MM-dd")   # 2025-01-15

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

Reactive binding
~~~~~~~~~~~~~~~~

Pass a ``Signal[str]`` via ``textsignal=`` to keep the field text in sync with
application state.

.. code-block:: python

   date_sig = bs.Signal("")
   bs.DateField(label="Pick a date", textsignal=date_sig)
   bs.Label(textsignal=date_sig, accent="secondary")

Handling changes
~~~~~~~~~~~~~~~~

``on_change()`` fires whenever the selected date changes — whether by keyboard
input, picker selection, or ``value=`` assignment.

.. code-block:: python

   df = bs.DateField(label="Appointment")
   df.on_change(lambda e: print("Selected:", df.value))

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

API
---

.. autoclass:: bootstack.widgets.datefield.DateField
   :members:
   :undoc-members:
   :inherited-members: PublicWidgetBase
   :exclude-members: tk

Full Example
------------

.. literalinclude:: ../../docs/examples/datefield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs