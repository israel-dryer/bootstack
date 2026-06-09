bootstack.validation
=====================

.. currentmodule:: bootstack.validation

Field and form validation. A ``ValidationRule`` checks a value and reports a
``ValidationResult`` — the building blocks behind a field's ``rules=`` and
``Form.validate()``.

For a task-oriented introduction — built-in rules, triggers, custom rules,
whole-form validation — see the :doc:`/reference/validation` guide.

.. autosummary::
   :toctree: generated
   :nosignatures:

   ValidationRule
   ValidationResult

Rule types
----------

The rule names accepted by ``ValidationRule`` and a field's
``add_validation_rule``.

.. autosummary::
   :toctree: generated
   :nosignatures:

   RuleType
