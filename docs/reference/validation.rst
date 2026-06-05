Validation
==========

Input fields can validate what the user types against a set of rules. A rule has
a type (``'required'``, ``'email'``, …), an optional message, and a trigger that
decides when it runs. Rules report a :class:`ValidationResult
<bootstack.validation.ValidationResult>`, and the field emits ``valid`` /
``invalid`` events you can listen to.

Adding rules to a field
-----------------------

Call ``add_validation_rule()`` on a field with a rule type and its options.
Rules run on blur (or as you type, depending on the rule) and stop at the first
failure:

.. code-block:: python

   email = bs.TextField(label="Email")
   email.add_validation_rule("required")
   email.add_validation_rule("email", message="Enter a valid email.")

   name = bs.TextField(label="Name")
   name.add_validation_rule("stringLength", min=2, max=50)

Built-in rule types and their options:

- ``'required'`` — value must not be empty.
- ``'email'`` — value must look like an email address.
- ``'stringLength'`` — ``min`` / ``max`` character count.
- ``'pattern'`` — ``pattern`` regex the value must match.
- ``'compare'`` — ``other_field`` whose value must match (e.g. confirm-password).
- ``'custom'`` — ``func`` callable ``(value: str) -> bool``.

All rules accept ``message`` (override the default text) and ``trigger``
(``'blur'`` default, ``'key'``, or ``'manual'``).

Reacting to validation
----------------------

Run all rules on demand with ``validate()`` (returns ``True`` if every rule
passes). Listen for outcomes with ``on_valid`` / ``on_invalid`` — both receive a
:class:`ValidationEvent <bootstack.events.ValidationEvent>` carrying the
``value``, ``is_valid``, and ``message``:

.. code-block:: python

   email.on_invalid(lambda e: print("nope:", e.message))
   email.on_valid(lambda e: print("ok:", e.value))

   if email.validate():
       submit()

Standalone rules
----------------

For validation outside a field, construct a :class:`ValidationRule
<bootstack.validation.ValidationRule>` and call ``validate()`` directly:

.. code-block:: python

   rule = bs.ValidationRule("stringLength", min=3, max=8)
   result = rule.validate("hi")
   result.is_valid     # False
   result.message      # the failure text

See also
--------

- :doc:`/reference/events` — the ``ValidationEvent`` payload and the ``on_*`` model.
- :doc:`/widgets/textfield` — the field widget these rules attach to.

API reference
-------------

.. autoclass:: bootstack.validation.ValidationRule
   :members:

.. autoclass:: bootstack.validation.ValidationResult
   :members:
