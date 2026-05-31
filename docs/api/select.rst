Select
======

A single-selection dropdown field with optional search filtering.

.. code-block:: python

   bs.Select(["Option A", "Option B", "Option C"])

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/selectfield-light.png"
        alt="Select demo — light theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/selectfield-dark.png"
        alt="Select demo — dark theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">

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

API
---

.. autoclass:: bootstack.widgets.select.Select
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/selectfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
