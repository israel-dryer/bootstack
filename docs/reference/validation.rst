Validation
==========

Input fields can check what the user types against a set of rules. A rule has a
type (``'required'``, ``'email'``, …), an optional custom message, and a
*trigger* that decides when it runs. Rules run in the order you add them and stop
at the first failure. The same rule engine also works standalone, with no widget
attached.

Rules validate the field's **typed value** — a ``custom`` rule on a
:class:`~bootstack.NumberField` receives a number, on a
:class:`~bootstack.DateField` a ``date``. So the rule *kind* matches the value
kind: the text rules (``'stringLength'``, ``'pattern'``, ``'email'``) apply to
text fields, ``'range'`` applies to numeric and date/time fields, and the rest
(``'required'``, ``'compare'``, ``'custom'``) apply anywhere. Attaching a rule to
a field whose value it can't validate raises an error, so the mismatch surfaces
when you write the code, not when the user types.

A field's validity is **reactive state** you can read, bind, or subscribe to
(``field.valid`` / ``field.error``), and it still emits ``valid`` / ``invalid``
events.

Adding rules to a field
-----------------------

Call ``add_validation_rule()`` on a field with a rule type and its options. Add
as many as you like — they are checked in order, and the first failure wins:

.. code-block:: python

   email = bs.TextField(label="Email")
   email.add_validation_rule("required")
   email.add_validation_rule("email", message="Enter a valid email.")

   name = bs.TextField(label="Name")
   name.add_validation_rule("stringLength", min=2, max=50)

Because ``'required'`` is the most common rule, fields accept it as a
``required=True`` constructor shortcut — it adds the rule and appends an asterisk
to the label:

.. code-block:: python

   email = bs.TextField(label="Email", required=True)   # same as add_validation_rule("required")

In a :class:`~bootstack.Form`, set ``required=True`` on the field's
:class:`~bootstack.FieldItem` for the same effect — see :doc:`/tasks/building-forms`.

Built-in rule types
-------------------

.. list-table::
   :header-rows: 1
   :widths: 18 42 40

   * - Type
     - Options
     - Checks that the value…
   * - ``'required'``
     - —
     - is not empty or whitespace.
   * - ``'email'``
     - —
     - looks like an email address. *(text fields)*
   * - ``'stringLength'``
     - ``min``, ``max``
     - has a length within the given bounds. *(text fields)*
   * - ``'pattern'``
     - ``pattern`` (regex)
     - matches the regular expression. *(text fields)*
   * - ``'range'``
     - ``min``, ``max``
     - falls within the given bounds — a number, or a ``date``/``time``.
       *(numeric and date/time fields)*
   * - ``'compare'``
     - ``other_field``
     - equals another field's value (confirm-password, etc.).
   * - ``'custom'``
     - ``func`` — ``(value) -> bool``
     - satisfies your own predicate.

Every rule also accepts ``message`` (override the default text) and ``trigger``
(see below).

Numeric and date bounds
~~~~~~~~~~~~~~~~~~~~~~~~~

A ``'range'`` rule bounds an ordered value — a number, a ``date``, or a
``time`` — with ``min`` and/or ``max``. Unlike a field's ``min_value`` /
``max_value`` (which *clamp* the input silently), a rule *reports* an
out-of-range value with a message:

.. code-block:: python

   age = bs.NumberField(label="Age")
   age.add_validation_rule("range", min=18, message="You must be 18 or older.")

   import datetime
   start = bs.DateField(label="Start date")
   start.add_validation_rule("range", min=datetime.date.today())

An empty field is not out of range — pair ``'range'`` with ``'required'`` if the
field must also be filled in.

.. note::

   ``'range'`` is for numeric and date/time fields; ``'stringLength'`` bounds the
   length of a **text** field. Each rule applies only where it makes sense, so
   ``age.add_validation_rule("stringLength", …)`` raises rather than silently
   measuring the number's digits.

Custom rules
~~~~~~~~~~~~

A ``'custom'`` rule runs any predicate that takes the field's typed value and
returns a bool — a string for a text field, a number for a
:class:`~bootstack.NumberField`, a ``date`` for a
:class:`~bootstack.DateField`. Pair it with a ``message`` so the user knows what
went wrong:

.. code-block:: python

   code = bs.TextField(label="Invite code")
   code.add_validation_rule(
       "custom",
       func=lambda v: v.isdigit() and len(v) == 6,
       message="The code is 6 digits.",
   )

   amount = bs.NumberField(label="Amount")
   amount.add_validation_rule(            # v is a number here, not text
       "custom",
       func=lambda v: v % 5 == 0,
       message="Enter a multiple of 5.",
   )

Confirming a second field
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ``'compare'`` rule passes only when the value matches ``other_field``. The
other field can be **another field widget**, a ``Signal``, or any zero-argument
callable — its value is read fresh each time the rule runs, so it always
compares against the current text:

.. code-block:: python

   password = bs.PasswordField(label="Password")
   password.add_validation_rule("stringLength", min=8)

   confirm = bs.PasswordField(label="Confirm password")
   confirm.add_validation_rule(
       "compare",
       other_field=password,                 # a field widget…
       message="Passwords don't match.",
   )

.. code-block:: python

   # …or compare against a Signal / callable instead of a widget
   pin = bs.Signal("")
   confirm.add_validation_rule("compare", other_field=pin)
   confirm.add_validation_rule("compare", other_field=lambda: expected_value())

When does a rule run?
---------------------

The ``trigger`` controls *when* a rule fires during normal typing. Each rule type
has a sensible default, which you can override per rule:

.. list-table::
   :header-rows: 1
   :widths: 18 82

   * - Trigger
     - Runs…
   * - ``'always'``
     - as the user types **and** when the field loses focus. Default for
       ``'required'``, ``'email'``, ``'pattern'``.
   * - ``'key'``
     - only as the user types.
   * - ``'blur'``
     - only when the field loses focus. Default for ``'stringLength'``,
       ``'range'``, and ``'compare'`` — they read better once the user has
       finished a field.
   * - ``'manual'``
     - never automatically — only when you call ``validate()`` yourself.
       Default for ``'custom'``.

Auto-validation is debounced, so a fast typist doesn't trigger a check on every
keystroke. Override the trigger when the default doesn't fit — for example, to
check a length rule live:

.. code-block:: python

   name.add_validation_rule("stringLength", min=2, max=50, trigger="always")

Reacting to validation
----------------------

A field's validity is reactive state. ``field.error`` is a ``Signal[str]`` — the
current message, or ``""`` when valid — and ``field.valid`` is a ``Signal[bool]``.
Bind the error straight to a label and it keeps itself in sync:

.. code-block:: python

   email = bs.TextField(label="Email")
   email.add_validation_rule("email", message="Enter a valid email.")

   bs.Label(textsignal=email.error, accent="danger")   # shows and clears itself

Read either signal on demand by calling it (``email.valid()``), or ``subscribe``
to run code on each change. The field already shows its own message below the
input, so binding ``error`` is for surfacing the state somewhere else (a summary,
a submit button's enabled state).

For a one-off reaction, the ``on_valid`` / ``on_invalid`` events still fire — each
receives a :class:`ValidationEvent <bootstack.events.ValidationEvent>` carrying
``value``, ``is_valid``, and ``message``:

.. code-block:: python

   email.on_invalid(lambda e: toast(e.message))

Run every rule on demand with ``validate()`` (regardless of trigger); it returns
``True`` when they all pass:

.. code-block:: python

   if email.validate():
       submit()

Validating a whole form before submit
-------------------------------------

A common pattern is to gate a submit button on every field passing. ``validate()``
runs all rules and surfaces the messages through the fields' own events, so the
guard itself stays short:

.. code-block:: python

   fields = [email, password, confirm]

   def on_submit():
       if all(f.validate() for f in fields):   # each shows its own error
           save(email.value, password.value)

   bs.Button("Create account", on_click=on_submit)

Because ``all()`` short-circuits, call ``validate()`` on each field in a list
comprehension first if you want *every* field to display its error at once:

.. code-block:: python

   results = [f.validate() for f in fields]   # validate them all
   if all(results):
       save(...)

A :class:`Form <bootstack.Form>` aggregates this for you. ``form.valid`` is a
reactive ``Signal[bool]`` AND-ed over its fields' own ``valid`` signals, so a
submit button can react to it directly — no manual list to keep in sync:

.. code-block:: python

   form = bs.Form(items=[
       {"key": "email", "required": True},
       {"key": "password", "dtype": "password", "required": True},
   ])
   submit = bs.Button("Create account", on_click=on_submit)

   def gate(ok):
       submit.disabled = not ok

   form.valid.subscribe(gate)

A field is valid until proven otherwise, so ``form.valid()`` reads ``True`` before
any rule has run — call ``form.validate()`` to force a full pass (for example, to
gate the button's initial state, or in ``on_submit``). ``form.errors`` is a live
dict of the failing fields keyed by field key, handy for a summary:

.. code-block:: python

   def on_submit():
       if not form.validate():
           toast(f"{len(form.errors)} field(s) need attention")
           return
       save(form.value)

Standalone rules
----------------

The rule engine doesn't need a widget. Construct a :class:`ValidationRule
<bootstack.validation.ValidationRule>` and call ``validate()`` directly — useful
for checking values from config, a CLI, or a background job:

.. code-block:: python

   from bootstack.validation import ValidationRule

   rule = ValidationRule("stringLength", min=3, max=8)
   result = rule.validate("hi")
   result.is_valid     # False
   result.message      # "Enter between 3 and 8 characters."

   ValidationRule("email").validate("a@b.co").is_valid       # True
   ValidationRule("compare", other_field="yes").validate("no").is_valid  # False

See also
--------

- :doc:`/reference/events` — the ``ValidationEvent`` payload and the ``on_*`` model.
- :doc:`/widgets/textfield` — the field widget these rules attach to.
- :doc:`/widgets/formdialog` — collects and validates a set of fields at once.

API reference
-------------

The complete reference for :class:`ValidationRule
<bootstack.validation.ValidationRule>` and :class:`ValidationResult
<bootstack.validation.ValidationResult>` lives in
:doc:`/api-reference/validation`. At a glance:

.. currentmodule:: bootstack.validation

.. autosummary::
   :nosignatures:

   ValidationRule
   ValidationResult
