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
   bs.TimeField(value=now, value_format="h:mm a")      # 2:30 PM

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

Pass a ``Signal[str]`` via ``textsignal=`` to keep the field text in sync with
application state.

.. code-block:: python

   time_sig = bs.Signal("")
   bs.TimeField(label="Pick a time", textsignal=time_sig)
   bs.Label(textsignal=time_sig, accent="secondary")

Handling changes
~~~~~~~~~~~~~~~~

``on_change()`` fires whenever the time value changes — whether by typing,
dropdown selection, or ``value=`` assignment.

.. code-block:: python

   tf = bs.TimeField(label="Start time")
   tf.on_change(lambda e: print("Selected:", tf.value))

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

API
---

.. autoclass:: bootstack.widgets.timefield.TimeField
   :members:
   :undoc-members:
   :inherited-members: PublicWidgetBase
   :exclude-members: tk

Full Example
------------

.. literalinclude:: ../../docs/examples/timefield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs