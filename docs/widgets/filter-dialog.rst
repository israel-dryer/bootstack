Filter Dialog
=============

``bs.ask_filter()`` opens a multi-select dialog and returns the chosen values.
``bs.FilterDialog`` gives the same dialog as a reusable object.

.. image:: /_static/examples/filter-dialog-hero-light.png
   :class: bs-screenshot-light bs-dialog-screenshot
   :alt: Filter Dialog — light theme

.. image:: /_static/examples/filter-dialog-hero-dark.png
   :class: bs-screenshot-dark bs-dialog-screenshot
   :alt: Filter Dialog — dark theme

Usage
-----

Basic usage
~~~~~~~~~~~

Pass a list of strings. ``ask_filter()`` returns the list of checked values,
or ``None`` if the user cancels.

.. code-block:: python

   countries = ["Australia", "Canada", "France", "Germany", "UK", "USA"]
   selected = bs.ask_filter(countries, title="Filter Countries")

Search and select-all
~~~~~~~~~~~~~~~~~~~~~

Enable the search box and/or the "Select All" checkbox:

.. code-block:: python

   selected = bs.ask_filter(
       countries,
       title="Filter Countries",
       enable_search=True,
       enable_select_all=True,
   )

Dict items
~~~~~~~~~~

Pass dicts to separate display labels from returned values, or to pre-check
some items:

.. code-block:: python

   items = [
       {"text": "Active",   "value": "active",   "selected": True},
       {"text": "Inactive", "value": "inactive"},
       {"text": "Pending",  "value": "pending",  "selected": True},
   ]
   selected = bs.ask_filter(items, title="Status Filter")
   # returns e.g. ['active', 'pending']

Each item dict supports:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Key
     - Description
   * - ``text``
     - Display label (required).
   * - ``value``
     - Value returned when checked. Defaults to ``text``.
   * - ``selected``
     - Initial check state. Defaults to ``False``.

Reusable dialog object
~~~~~~~~~~~~~~~~~~~~~~

Use ``bs.FilterDialog`` to inspect the result after ``show()``:

.. code-block:: python

   dlg = bs.FilterDialog(
       title="Status Filter",
       items=items,
       enable_select_all=True,
   )
   dlg.show()

   if dlg.result is not None:
       apply_filter(dlg.result)

See also
--------

:doc:`input-dialogs` — ``ask_item()`` for choosing a single item from a list.

:doc:`dialog` — ``Dialog`` for fully custom dialog layouts.

API
---

.. autofunction:: bootstack.widgets.dialogs.ask_filter

.. autoclass:: bootstack.widgets.dialogs.FilterDialog
   :members:

Full Example
------------

.. literalinclude:: ../../docs/examples/filter-dialog.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs