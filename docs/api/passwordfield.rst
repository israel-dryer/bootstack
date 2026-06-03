PasswordField
=============

Masked text input for password entry with an optional visibility toggle.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/passwordfield-hero-light.png"
        alt="PasswordField demo — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/passwordfield-hero-dark.png"
        alt="PasswordField demo — dark theme"
        style="max-width:100%;">

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

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/passwordfield-toggle-light.png"
        alt="PasswordField visibility toggle — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/passwordfield-toggle-dark.png"
        alt="PasswordField visibility toggle — dark theme"
        style="max-width:100%;">

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

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/passwordfield-states-light.png"
        alt="PasswordField states — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/passwordfield-states-dark.png"
        alt="PasswordField states — dark theme"
        style="max-width:100%;">

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

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/passwordfield-validation-light.png"
        alt="PasswordField validation — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/passwordfield-validation-dark.png"
        alt="PasswordField validation — dark theme"
        style="max-width:100%;">

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`textfield` — plain text input
* :doc:`numberfield` — numeric input with optional range constraints

API
---

.. autoclass:: bootstack.widgets.passwordfield.PasswordField
   :members:
   :undoc-members:
   :inherited-members: FieldAddonMixin
   :exclude-members: tk

Full Example
------------

.. literalinclude:: ../../docs/examples/passwordfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
