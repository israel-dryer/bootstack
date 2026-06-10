Input Dialogs
=============

Convenience functions for collecting a single value from the user. Each opens
a modal dialog, waits for input, and returns the value (or ``None`` if canceled).

.. image:: /_static/examples/input-dialogs-hero-light.png
   :class: bs-screenshot-light bs-dialog-screenshot
   :alt: Input Dialogs — text input dialog, light theme

.. image:: /_static/examples/input-dialogs-hero-dark.png
   :class: bs-screenshot-dark bs-dialog-screenshot
   :alt: Input Dialogs — text input dialog, dark theme

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

.. image:: /_static/examples/input-dialogs-date-light.png
   :class: bs-screenshot-light bs-dialog-screenshot
   :alt: Input Dialogs — date picker dialog, light theme

.. image:: /_static/examples/input-dialogs-date-dark.png
   :class: bs-screenshot-dark bs-dialog-screenshot
   :alt: Input Dialogs — date picker dialog, dark theme

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

The complete reference for the ``ask_*`` input verbs lives on the
:doc:`Dialogs </api-reference/dialogs>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.ask_string
   ~bootstack.ask_integer
   ~bootstack.ask_float
   ~bootstack.ask_item
   ~bootstack.ask_date
   ~bootstack.ask_date_range

Full Example
------------

.. literalinclude:: ../../docs/examples/input-dialogs.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs