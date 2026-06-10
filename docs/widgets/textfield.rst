TextField
=========

Single-line text input with optional label, helper text, placeholder,
validation, and reactive signal binding.

.. image:: /_static/examples/textfield-hero-light.png
   :class: bs-screenshot-light
   :alt: TextField demo — light theme

.. image:: /_static/examples/textfield-hero-dark.png
   :class: bs-screenshot-dark
   :alt: TextField demo — dark theme

Usage
-----

Basic
~~~~~

.. code-block:: python

   bs.TextField(placeholder="Type something…")

Label and message
~~~~~~~~~~~~~~~~~

Use ``label=`` for a field title and ``message=`` for helper text below.

.. code-block:: python

   bs.TextField(
       label="Email address",
       placeholder="you@example.com",
       message="We'll never share your email.",
   )

Required
~~~~~~~~

Set ``required=True`` to mark the field visually and prevent empty submission.

.. code-block:: python

   bs.TextField(label="Username",     required=True, placeholder="Required field")
   bs.TextField(label="Email address", placeholder="Optional field")

.. image:: /_static/examples/textfield-required-light.png
   :class: bs-screenshot-light
   :alt: TextField required — light theme

.. image:: /_static/examples/textfield-required-dark.png
   :class: bs-screenshot-dark
   :alt: TextField required — dark theme

Value formatting
~~~~~~~~~~~~~~~~

Use ``value_format=`` to display the value with a locale-aware ICU pattern.
The raw string value is preserved internally; only the display changes.
Requires localization to be enabled.

.. code-block:: python

   bs.TextField(value_format="#,##0.00", label="Decimal")
   bs.TextField(value_format="percent",  label="Percent")
   bs.TextField(value_format="currency", label="Currency")
   bs.TextField(value_format="yyyy-MM-dd", label="Date")

.. image:: /_static/examples/textfield-value-format-light.png
   :class: bs-screenshot-light
   :alt: TextField value formatting — light theme

.. image:: /_static/examples/textfield-value-format-dark.png
   :class: bs-screenshot-dark
   :alt: TextField value formatting — dark theme

States
~~~~~~

.. code-block:: python

   bs.TextField(value="Editable",  label="Normal")
   bs.TextField(value="Read only", label="Read only", read_only=True)
   bs.TextField(value="Disabled",  label="Disabled",  disabled=True)

.. image:: /_static/examples/textfield-states-light.png
   :class: bs-screenshot-light
   :alt: TextField states — light theme

.. image:: /_static/examples/textfield-states-dark.png
   :class: bs-screenshot-dark
   :alt: TextField states — dark theme

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal[str]`` with ``textsignal=``. The field and signal stay in
sync automatically — typing updates the signal, setting the signal updates
the field.

.. code-block:: python

   name = bs.Signal("World")
   bs.TextField(label="Name", textsignal=name)
   bs.Label(textsignal=name, accent="secondary")   # updates as you type

Live input events
~~~~~~~~~~~~~~~~~

``on_input()`` fires on every keystroke. Use it for real-time feedback,
character counting, or live search — anything that needs to respond to
typing, not just field exit.

.. code-block:: python

   count = bs.Label("0 / 100", accent="secondary", font="caption")
   field = bs.TextField(placeholder="Type…")

   def _update_count(e):
       count.text = f"{len(field.value)} / 100"

   field.on_input(_update_count)

   # Or as a debounced Stream
   field.on_input().debounce(300).listen(lambda e: search(field.value))

Submit on Enter
~~~~~~~~~~~~~~~

.. code-block:: python

   field = bs.TextField(placeholder="Search…")
   field.on_submit(lambda e: run_search(field.value))

Validation
~~~~~~~~~~

Attach rules with ``add_validation_rule()``. Rules run on the configured
trigger (``'blur'``, ``'key'``, or ``'manual'``).

.. code-block:: python

   field = bs.TextField(label="Username")
   field.add_validation_rule(
       "stringLength",
       message="Must be at least 3 characters.",
       min=3,
       trigger="blur",
   )

   # Explicit validation check
   is_valid = field.validate()

.. image:: /_static/examples/textfield-validation-light.png
   :class: bs-screenshot-light
   :alt: TextField validation — light theme

.. image:: /_static/examples/textfield-validation-dark.png
   :class: bs-screenshot-dark
   :alt: TextField validation — dark theme

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

The complete reference for :class:`TextField <bootstack.TextField>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.TextField

Full Example
------------

.. literalinclude:: ../../docs/examples/textfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
