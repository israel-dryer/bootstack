Calendar
========

An inline calendar for single-date or date-range selection.

.. image:: /_static/examples/calendarwidget-hero-light.png
   :class: bs-screenshot-light
   :alt: Calendar — light theme

.. image:: /_static/examples/calendarwidget-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Calendar — dark theme

Usage
-----

Basic
~~~~~

The calendar is always visible — it is not a popup. Pass a
:class:`datetime.date`, :class:`datetime.datetime`, or an ISO string
as ``value=``.

.. code-block:: python

   from datetime import date

   bs.Calendar()                            # today's month, nothing selected
   bs.Calendar(value=date(2026, 5, 15))     # specific date pre-selected
   bs.Calendar(value="2026-05-15")          # ISO string accepted

Range selection
~~~~~~~~~~~~~~~

Set ``selection_mode='range'`` to select a start–end span. The calendar
shows two months side by side. The first click sets the start date;
the second click sets the end date.

.. code-block:: python

   bs.Calendar(
       selection_mode="range",
       start_date=date(2026, 5, 20),
       end_date=date(2026, 6, 10),
   )

.. image:: /_static/examples/calendarwidget-range-light.png
   :class: bs-screenshot-light
   :alt: Calendar range selection — light theme

.. image:: /_static/examples/calendarwidget-range-dark.png
   :class: bs-screenshot-dark
   :alt: Calendar range selection — dark theme

Accent colors
~~~~~~~~~~~~~

``accent=`` controls the color of selected dates and range highlights.

.. code-block:: python

   bs.Calendar(accent="primary")    # default
   bs.Calendar(accent="success")
   bs.Calendar(accent="danger")

Min / max bounds
~~~~~~~~~~~~~~~~

Dates outside the bounds are disabled and month navigation is blocked
at the limits.

.. code-block:: python

   bs.Calendar(
       min_date=date(2026, 5, 1),
       max_date=date(2026, 5, 31),
   )

Disabled dates
~~~~~~~~~~~~~~

Individual dates can be disabled regardless of the min/max range.

.. code-block:: python

   bs.Calendar(disabled_dates=[date(2026, 5, 4), date(2026, 5, 11)])

Week numbers
~~~~~~~~~~~~

Display ISO 8601 week numbers in the leftmost column.

.. code-block:: python

   bs.Calendar(value=date(2026, 5, 15), show_week_numbers=True)

.. image:: /_static/examples/calendarwidget-week-numbers-light.png
   :class: bs-screenshot-light
   :alt: Calendar week numbers — light theme

.. image:: /_static/examples/calendarwidget-week-numbers-dark.png
   :class: bs-screenshot-dark
   :alt: Calendar week numbers — dark theme

First weekday
~~~~~~~~~~~~~

Override the locale default for the first column (0=Monday, 6=Sunday).

.. code-block:: python

   bs.Calendar(first_weekday=6)   # week starts on Sunday

Events
~~~~~~

``on_date_selected()`` fires after every click. In range mode it fires
twice — once when the start is set (``end`` is ``None``) and again when
the end is set.

.. code-block:: python

   cal = bs.Calendar()

   # Single mode
   cal.on_date_selected(lambda e: print("selected:", cal.value))

   # Range mode — wait for a complete range
   cal = bs.Calendar(selection_mode="range")
   def _on_select(e):
       start, end = cal.range
       if end is not None:
           print(f"range: {start} → {end}")
   cal.on_date_selected(_on_select)

   # As a Stream
   cal.on_date_selected().listen(lambda e: refresh(cal.value))

Programmatic control
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   cal = bs.Calendar()

   cal.value = date(2026, 6, 1)        # set selected date
   cal.get()                            # → date(2026, 6, 1)
   cal.set(date(2026, 6, 15))          # set without firing event

   # Range mode
   cal.range = (date(2026, 6, 1), date(2026, 6, 14))
   cal.get_range()                      # → (date(...), date(...))
   cal.set_range(date(2026, 6, 1), date(2026, 6, 14))

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

.. autoclass:: bootstack.widgets.calendar.Calendar
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/calendarwidget.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs