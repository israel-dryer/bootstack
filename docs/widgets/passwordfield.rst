PasswordField
=============

Masked text input for password entry with an optional visibility toggle.

.. image:: /_static/examples/passwordfield-hero-light.png
   :class: bs-screenshot-light
   :alt: PasswordField demo — light theme

.. image:: /_static/examples/passwordfield-hero-dark.png
   :class: bs-screenshot-dark
   :alt: PasswordField demo — dark theme

A password field is a single-line text input that masks what the user types.
Read or set the secret through ``field.value`` — always the unmasked string — or
bind it with ``textsignal=``. Users can briefly reveal the input by holding the
eye toggle, and you can drive masking from code with ``reveal()`` / ``hide()``.
Validation runs against the typed value, exactly like a plain
:doc:`text field <textfield>`.

Usage
-----

Basic
~~~~~

.. code-block:: python

   bs.PasswordField(placeholder="Enter password…")

Label and message
~~~~~~~~~~~~~~~~~

Use ``label=`` for a field title and ``message=`` for helper text below.

.. code-block:: python

   bs.PasswordField(
       label="Password",
       placeholder="Enter password…",
       message="Must be at least 8 characters.",
   )

Required
~~~~~~~~

Set ``required=True`` to mark the field visually and prevent empty submission.

.. code-block:: python

   bs.PasswordField(label="Password", required=True)

Visibility toggle
~~~~~~~~~~~~~~~~~

The eye-icon button is shown by default and reveals the password while held.
Disable it with ``show_visibility_toggle=False``.

.. code-block:: python

   bs.PasswordField(label="With toggle", value="secret123")
   bs.PasswordField(label="No toggle",   value="secret123", show_visibility_toggle=False)

.. image:: /_static/examples/passwordfield-toggle-light.png
   :class: bs-screenshot-light
   :alt: PasswordField visibility toggle — light theme

.. image:: /_static/examples/passwordfield-toggle-dark.png
   :class: bs-screenshot-dark
   :alt: PasswordField visibility toggle — dark theme

Programmatic reveal / hide
~~~~~~~~~~~~~~~~~~~~~~~~~~

Call ``reveal()`` and ``hide()`` to control masking in code — useful for a
"show password" checkbox pattern.

.. code-block:: python

   field = bs.PasswordField(label="Password", show_visibility_toggle=False)

   def _toggle_reveal(e):
       if checkbox.value:
           field.reveal()
       else:
           field.hide()

   checkbox = bs.Checkbox("Show password", on_change=_toggle_reveal)

Custom mask character
~~~~~~~~~~~~~~~~~~~~~

The default mask is ``'•'``. Supply any single character via ``mask=``.

.. code-block:: python

   bs.PasswordField(mask="*")

States
~~~~~~

.. code-block:: python

   bs.PasswordField(value="secret123", label="Normal")
   bs.PasswordField(value="secret123", label="Read only", read_only=True)
   bs.PasswordField(value="secret123", label="Disabled",  disabled=True)

.. image:: /_static/examples/passwordfield-states-light.png
   :class: bs-screenshot-light
   :alt: PasswordField states — light theme

.. image:: /_static/examples/passwordfield-states-dark.png
   :class: bs-screenshot-dark
   :alt: PasswordField states — dark theme

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal[str]`` with ``textsignal=``. The field and signal stay in
sync automatically — typing updates the signal, setting the signal updates
the field.

.. code-block:: python

   password = bs.Signal("")
   bs.PasswordField(label="Password", textsignal=password)
   password.subscribe(lambda v: validate_strength(v))

Submit on Enter
~~~~~~~~~~~~~~~

.. code-block:: python

   field = bs.PasswordField(placeholder="Password…")
   field.on_submit(lambda e: attempt_login(field.value))

Validation
~~~~~~~~~~

Attach rules with ``add_validation_rule()``. Rules run on the configured
trigger (``'blur'``, ``'key'``, or ``'manual'``).

.. code-block:: python

   field = bs.PasswordField(label="Password")
   field.add_validation_rule(
       "stringLength",
       message="Password must be at least 8 characters.",
       min=8,
       trigger="blur",
   )

   # Explicit validation check
   is_valid = field.validate()

.. image:: /_static/examples/passwordfield-validation-light.png
   :class: bs-screenshot-light
   :alt: PasswordField validation — light theme

.. image:: /_static/examples/passwordfield-validation-dark.png
   :class: bs-screenshot-dark
   :alt: PasswordField validation — dark theme

Validity is reactive state. ``field.valid`` is a ``Signal[bool]`` and
``field.error`` a ``Signal[str]`` (the current message, ``""`` when valid) — bind
the error to a label and it keeps itself in sync, or gate the submit button off
``field.valid``:

.. code-block:: python

   bs.Label(textsignal=field.error, accent="danger")   # shows and clears itself

.. note::

   The full rule taxonomy (``stringLength``, ``pattern``, ``custom``, …) and
   aggregating a whole form's validity live in the
   :doc:`Validation </reference/validation>` guide.

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`textfield` — plain text input
* :doc:`numberfield` — numeric input with optional range constraints
* :doc:`Validation </reference/validation>` — the full rule set and form-level validity
* :doc:`Composing Fields </tasks/composing-fields>` — add buttons or icons inside a field, and reusable field types
* :doc:`Signals </reference/signals>` — the reactive binding behind ``textsignal=``

API
---

The complete reference for :class:`PasswordField <bootstack.PasswordField>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.PasswordField

Full Example
------------

.. literalinclude:: ../../docs/examples/passwordfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
