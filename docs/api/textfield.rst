TextField
=========

Single-line text input with optional label, helper text, placeholder,
validation, and reactive signal binding.

.. code-block:: python

   bs.TextField(label="Email", placeholder="you@example.com")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/textfield-light.png"
        alt="TextField demo — light theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/textfield-dark.png"
        alt="TextField demo — dark theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">

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

   bs.TextField(label="Username", required=True)

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

States
~~~~~~

.. code-block:: python

   bs.TextField(value="Normal text")
   bs.TextField(value="Cannot edit", read_only=True)
   bs.TextField(value="Non-interactive", disabled=True)

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

   from bootstack.validation import ValidationRule

   field = bs.TextField(label="Username")
   field.add_validation_rule(ValidationRule(
       "stringLength",
       message="Must be at least 3 characters.",
       min=3,
       trigger="blur",
   ))

   # Explicit validation check
   is_valid = field.validate()

API
---

.. autoclass:: bootstack.widgets.textfield.TextField
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/textfield.py
   :language: python
   :start-after: import bootstack as bs
