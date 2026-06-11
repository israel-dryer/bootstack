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

Option values
~~~~~~~~~~~~~

An option's displayed label can differ from its stored value. Each option is a
plain string, a ``(text, value)`` tuple, or a ``{"text": ..., "value": ...}``
dict. ``value=``, ``.value``, and the change event all work in *value-space* —
the value, not the label. The label currently shown is available as ``.text``.

.. code-block:: python

   theme = bs.Select(
       [("Light theme", "light"), ("Dark theme", "dark"), {"text": "Follow system", "value": "auto"}],
       value="dark",
   )
   theme.value            # -> "dark"          (the value)
   theme.text             # -> "Dark theme"    (the displayed label)
   theme.value = "auto"   # selects "Follow system"
   theme.on_change(lambda e: apply_theme(e.value))

   theme.options          # -> [{"text": "Light theme", "value": "light"}, ...]

Setting ``.value`` to something that is not one of the options raises
``ValueError`` (unless ``allow_custom_values=True``, where a typed value is kept
as its own text).

Carrying extra data (the data bag)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The dict form is a *data bag* — alongside the recognized keys (``text``,
``value``, and the per-option ``icon``/``disabled``), any other key you add rides
along as carried data. Read the whole selected record, indexed by key, via
``.selection``:

.. code-block:: python

   country = bs.Select(options=[
       {"text": "Canada", "value": "CA", "phone": "+1"},
       {"text": "Japan",  "value": "JP", "phone": "+81"},
   ], value="JP")

   country.value             # -> "JP"
   country.selection         # -> {"text": "Japan", "value": "JP", "phone": "+81"}
   country.selection["phone"]  # -> "+81"

   country.on_change(lambda e: dial(country.selection["phone"]))

``.selection`` is the selected option's full dict (the same shape you'd get from a
``ListView`` row), or ``None`` when nothing is selected. Unrecognized keys are
*accepted, not validated* — the dict route is opt-in, so a mistyped key rides
along silently rather than raising.

Two of the recognized keys change how an option is *presented*: ``icon`` renders a
glyph beside the option's label in the popup, and ``disabled`` greys the row out
and makes it non-selectable (keyboard navigation and search auto-select skip it
too). Per-option ``disabled`` is independent of the widget-level ``disabled=``
that locks the whole control:

.. code-block:: python

   bs.Select(options=[
       {"text": "Free",       "value": "free",  "icon": "gift"},
       {"text": "Pro",        "value": "pro",   "icon": "star"},
       {"text": "Enterprise", "value": "ent",   "icon": "buildings", "disabled": True},
   ], value="free")

Setting a disabled option's value programmatically still works — ``disabled`` only
blocks *user* selection.

Grouping
~~~~~~~~

Pass ``group_by="field"`` to cluster the popup under section headers, where
``field`` is any key your options carry — often a category that already lives in
your data. Grouping is purely presentational: ``value``, ``.selection``, and
``.options`` are unaffected, and the grouping field rides along in the data bag.

.. code-block:: python

   bs.Select(
       options=[
           {"text": "Apple",    "value": "apple",    "category": "Fruit"},
           {"text": "Banana",   "value": "banana",   "category": "Fruit"},
           {"text": "Carrot",   "value": "carrot",   "category": "Vegetable"},
           {"text": "Basil",    "value": "basil",    "category": "Herb"},
       ],
       group_by="category",
       label="Ingredient",
   )

Groups appear in first-appearance order; an option that lacks the field renders
without a header. Header text is shown verbatim — it is never re-cased or
otherwise transformed, so ``.selection`` still returns the original value
(``{..., "category": "Fruit"}``).

.. image:: /_static/examples/selectfield-grouping-light.png
   :class: bs-screenshot-light
   :alt: Select grouping — light theme

.. image:: /_static/examples/selectfield-grouping-dark.png
   :class: bs-screenshot-dark
   :alt: Select grouping — dark theme

Limiting the popup height
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The popup grows to fit its options up to a built-in cap, then scrolls. Set
``max_visible_items=`` to cap it at roughly that many option rows — handy for long
lists. Group headers and separators count toward the height, so the number is
approximate.

.. code-block:: python

   countries = ["Canada", "France", "Germany", "Japan", "United States", "..."]
   bs.Select(countries, label="Country", max_visible_items=8)

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
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Select

Full Example
------------

.. literalinclude:: ../../docs/examples/selectfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs