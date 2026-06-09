Select
======

A single-selection dropdown field with optional search filtering.

.. image:: /_static/examples/selectfield-hero-light.png
   :class: bs-screenshot-light
   :alt: Select — light theme

.. image:: /_static/examples/selectfield-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Select — dark theme

Usage
-----

Basic
~~~~~

.. code-block:: python

   bs.Select(["Red", "Green", "Blue"])
   bs.Select(["Red", "Green", "Blue"], value="Green")

Label and message
~~~~~~~~~~~~~~~~~

.. code-block:: python

   bs.Select(
       ["Option A", "Option B", "Option C"],
       label="Choose an option",
       message="Select the option that best applies.",
   )

Required
~~~~~~~~

.. code-block:: python

   bs.Select(["Red", "Green", "Blue"], label="Color", required=True)

Searchable
~~~~~~~~~~

Set ``searchable=True`` to filter options as the user types.

.. code-block:: python

   countries = ["Canada", "France", "Germany", "Japan", "United States"]
   bs.Select(countries, label="Country", searchable=True)

Custom values
~~~~~~~~~~~~~

Set ``allow_custom_values=True`` to accept typed values not in the list.

.. code-block:: python

   bs.Select(["Red", "Green", "Blue"], allow_custom_values=True)

States
~~~~~~

.. code-block:: python

   bs.Select(["A", "B", "C"], value="A", label="Normal")
   bs.Select(["A", "B", "C"], value="A", label="Read only",  read_only=True)
   bs.Select(["A", "B", "C"], value="A", label="Disabled",   disabled=True)

.. image:: /_static/examples/selectfield-states-light.png
   :class: bs-screenshot-light
   :alt: Select states — light theme

.. image:: /_static/examples/selectfield-states-dark.png
   :class: bs-screenshot-dark
   :alt: Select states — dark theme

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal[str]`` with ``signal=``. The field and signal stay in sync.

.. code-block:: python

   color = bs.Signal("Red")
   bs.Select(["Red", "Green", "Blue"], signal=color)
   color.subscribe(lambda v: apply_color(v))

Updating options at runtime
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Assign to ``.options`` to replace the list dynamically.

.. code-block:: python

   sel = bs.Select(["A", "B", "C"])
   sel.options = ["X", "Y", "Z"]

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

The complete reference for :class:`Select <bootstack.Select>` lives on the
:doc:`bootstack </api-reference/bootstack>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Select

Full Example
------------

.. literalinclude:: ../../docs/examples/selectfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs