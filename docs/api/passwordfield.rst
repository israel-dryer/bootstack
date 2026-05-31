PasswordField
=============

Masked text input for password entry with an optional visibility toggle.

.. code-block:: python

   bs.PasswordField(label="Password", placeholder="Enter password…")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/passwordfield-light.png"
        alt="PasswordField demo — light theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/passwordfield-dark.png"
        alt="PasswordField demo — dark theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">

Usage
-----

Basic
~~~~~

.. code-block:: python

   bs.PasswordField(placeholder="Enter password…")

Label and message
~~~~~~~~~~~~~~~~~

.. code-block:: python

   bs.PasswordField(
       label="Password",
       placeholder="Enter password…",
       message="Must be at least 8 characters.",
   )

Required
~~~~~~~~

.. code-block:: python

   bs.PasswordField(label="Password", required=True)

Visibility toggle
~~~~~~~~~~~~~~~~~

The eye-icon button is shown by default and reveals the password while held.
Disable it with ``show_visibility_toggle=False``.

.. code-block:: python

   bs.PasswordField(label="With toggle")        # default
   bs.PasswordField(label="No toggle", show_visibility_toggle=False)

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

States
~~~~~~

.. code-block:: python

   bs.PasswordField(value="secret", label="Normal")
   bs.PasswordField(value="secret", label="Read only", read_only=True)
   bs.PasswordField(value="secret", label="Disabled", disabled=True)

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal[str]`` with ``textsignal=``. The field and signal stay in
sync automatically.

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

.. code-block:: python

   from bootstack.validation import ValidationRule

   field = bs.PasswordField(label="Password")
   field.add_validation_rule(ValidationRule(
       "stringLength",
       message="Password must be at least 8 characters.",
       min=8,
       trigger="blur",
   ))

Custom mask character
~~~~~~~~~~~~~~~~~~~~~

The default mask is ``'•'``. Supply any single character via ``mask=``.

.. code-block:: python

   bs.PasswordField(mask="*")

API
---

.. autoclass:: bootstack.widgets.passwordfield.PasswordField
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/passwordfield.py
   :language: python
   :start-after: import bootstack as bs