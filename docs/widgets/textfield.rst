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

A field keeps three things distinct: the ``label`` beside it, the ``value`` you
read and write in code, and the display ``text`` the user sees. Read the current
input with ``field.value``, or bind a :doc:`Signal </reference/signals>` with
``textsignal=`` to keep a variable and the field in lockstep. Input events fire in
two beats — ``on_input`` on every keystroke, ``on_change`` once the value is
committed (on blur or Enter) — so you choose live feedback or settled value per
handler.

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

   bs.TextField(value="1234.5",     value_format="#,##0.00",  label="Decimal")
   bs.TextField(value="0.42",       value_format="percent",   label="Percent")
   bs.TextField(value="9.99",       value_format="currency",  label="Currency")
   bs.TextField(value="2024-06-01", value_format="yyyy-MM-dd", label="Date")

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

Committed changes
~~~~~~~~~~~~~~~~~

``on_change()`` fires once the value is *committed* — when the field loses focus
or the user presses Enter — not on every keystroke. Reach for it when the work
is expensive or should run on the settled value (saving, recomputing a total).
The handler receives a :class:`~bootstack.events.ChangeEvent` with the parsed
``value`` and the previous one.

.. code-block:: python

   bs.TextField(label="Display name").on_change(lambda e: save(e.value))

Submit on Enter
~~~~~~~~~~~~~~~

.. code-block:: python

   field = bs.TextField(placeholder="Search…")
   field.on_submit(lambda e: run_search(field.value))

Validation
~~~~~~~~~~

Attach rules with ``add_validation_rule()``. Rules run on the configured
trigger (``'blur'``, ``'key'``, or ``'manual'``), and validate the field's
**typed value** — for a plain text field that is the string itself.

.. code-block:: python

   field = bs.TextField(label="Username")
   field.add_validation_rule(
       "stringLength",
       message="Must be at least 3 characters.",
       min=3,
       trigger="blur",
   )

   is_valid = field.validate()   # run every rule on demand

.. image:: /_static/examples/textfield-validation-light.png
   :class: bs-screenshot-light
   :alt: TextField validation — light theme

.. image:: /_static/examples/textfield-validation-dark.png
   :class: bs-screenshot-dark
   :alt: TextField validation — dark theme

Validity is reactive state. ``field.valid`` is a ``Signal[bool]`` and
``field.error`` a ``Signal[str]`` (the current message, ``""`` when valid) — bind
the error straight to a label and it keeps itself in sync, or drive a submit
button off ``field.valid``:

.. code-block:: python

   bs.Label(textsignal=field.error, accent="danger")   # shows and clears itself

.. note::

   This is the field-level slice. The rule taxonomy (text rules vs value rules),
   the ``range`` rule, ``compare`` and ``custom`` rules, how the typed value is
   resolved, and aggregating a whole form's validity all live in the
   :doc:`Validation </reference/validation>` guide.

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

- :doc:`Validation </reference/validation>` — the full rule set, typed-value model,
  and form-level validity.
- :doc:`Composing Fields </tasks/composing-fields>` — add buttons or icons inside a
  field, and subclass it into a reusable type.
- :doc:`/widgets/passwordfield` — a text field with a built-in mask and reveal toggle.
- :doc:`/widgets/numberfield`, :doc:`/widgets/datefield` — typed siblings for numeric
  and date input.
- :doc:`Signals </reference/signals>` — the reactive binding behind ``textsignal=``.

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
