Input Dialogs
=============

Convenience functions for collecting a single value from the user. Each opens
a modal dialog, waits for input, and returns the value (or ``None`` if canceled).

.. code-block:: python

   name = bs.ask_string("Enter your name:")
   age  = bs.ask_integer("Enter age:", min_value=0, max_value=120)

.. raw:: html

   <img class="bs-screenshot-light bs-dialog-screenshot"
        src="/_static/examples/input-dialogs-light.png"
        alt="Input Dialogs demo — light theme"
        style="max-width:100%; margin:1rem 0;">
   <img class="bs-screenshot-dark bs-dialog-screenshot"
        src="/_static/examples/input-dialogs-dark.png"
        alt="Input Dialogs demo — dark theme"
        style="max-width:100%; margin:1rem 0;">

Usage
-----

Ask for text
~~~~~~~~~~~~

``bs.ask_string()`` shows a text field. Returns the entered string, or ``None``
if canceled.

.. code-block:: python

   name = bs.ask_string("Enter your name:", title="Name")
   if name:
       greet(name)

Pass ``value=`` to pre-fill the field:

.. code-block:: python

   new_name = bs.ask_string("Rename:", value=current_name)

Ask for a number
~~~~~~~~~~~~~~~~

``bs.ask_integer()`` and ``bs.ask_float()`` show a numeric field with an
optional stepper, range validation, and display format. Both return ``None``
if canceled.

.. code-block:: python

   age   = bs.ask_integer("Enter age:", min_value=0, max_value=120)
   price = bs.ask_float("Enter price:", min_value=0.0, step=0.5)

Ask from a list
~~~~~~~~~~~~~~~

``bs.ask_item()`` shows a searchable dropdown. Returns the selected string,
or ``None`` if canceled.

.. code-block:: python

   country = bs.ask_item(
       "Select your country:",
       ["Canada", "UK", "USA", "Other"],
       title="Country",
   )

Ask for a date
~~~~~~~~~~~~~~

``bs.ask_date()`` opens a calendar picker. Returns a ``datetime.date``, or
``None`` if canceled.

.. code-block:: python

   from datetime import date

   picked = bs.ask_date(title="Select date", value=date.today())

Restrict the selectable range with ``min_date=`` and ``max_date=``:

.. code-block:: python

   deadline = bs.ask_date(title="Pick a deadline", min_date=date.today())

Ask for a date range
~~~~~~~~~~~~~~~~~~~~

``bs.ask_date_range()`` opens the calendar in range-selection mode. Returns a
``(start, end)`` tuple of ``date`` objects, or ``None`` if canceled.

.. code-block:: python

   result = bs.ask_date_range(title="Report period")
   if result:
       start, end = result

See also
--------

:doc:`message-dialogs` — ``alert()`` and ``confirm()`` for notifications and yes/no prompts.

:doc:`color-dialog` — ``ask_color()`` for choosing a color.

:doc:`font-dialog` — ``ask_font()`` for selecting a font.

:doc:`filter-dialog` — ``ask_filter()`` for multi-select from a list.

API
---

.. autofunction:: bootstack.widgets.dialogs.ask_string

.. autofunction:: bootstack.widgets.dialogs.ask_integer

.. autofunction:: bootstack.widgets.dialogs.ask_float

.. autofunction:: bootstack.widgets.dialogs.ask_item

.. autofunction:: bootstack.widgets.dialogs.ask_date

.. autofunction:: bootstack.widgets.dialogs.ask_date_range

Full Example
------------

.. literalinclude:: ../../docs/examples/input-dialogs.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs