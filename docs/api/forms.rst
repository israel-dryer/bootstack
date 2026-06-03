.. _forms:

Form
====

``bs.Form`` builds a data-entry layout from a dict or an explicit list of field
definitions. Fields are placed on a grid; :class:`GroupItem
<bootstack.widgets.form.GroupItem>` creates labeled sections and
:class:`TabsItem <bootstack.widgets.form.TabsItem>` creates a tabbed layout.

.. code-block:: python

   bs.Form(data={"name": "", "email": "", "role": "Editor"})

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/forms-light.png"
        alt="Form demo — light theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/forms-dark.png"
        alt="Form demo — dark theme"
        style="max-width:100%; border-radius:6px; margin:1rem 0;">

Usage
-----

Auto-generated fields
~~~~~~~~~~~~~~~~~~~~~

Pass a dict to ``data=``. Keys become field labels; value types determine the
editor widget automatically:

.. code-block:: python

   bs.Form(
       data={
           "name": "Alice Smith",     # str  → text entry
           "email": "alice@example.com",
           "age": 30,                 # int  → numeric entry
           "active": True,            # bool → checkbox
       },
   )

The returned ``value`` dict has the same keys as ``data``, filled with
the user's current input.

Multiple columns
~~~~~~~~~~~~~~~~

Use ``col_count=`` to distribute fields across multiple columns:

.. code-block:: python

   bs.Form(
       data={
           "street": "",
           "city": "",
           "state": "",
           "zip": "",
       },
       col_count=2,
   )

Explicit fields
~~~~~~~~~~~~~~~

Use :class:`FieldItem <bootstack.widgets.form.FieldItem>` for full control over
each field — label, type hint, editor, and grid placement:

.. code-block:: python

   bs.Form(
       items=[
           bs.FieldItem(key="username", label="Username"),
           bs.FieldItem(key="password", label="Password", dtype="password"),
           bs.FieldItem(key="role", label="Role",
                        editor="select",
                        editor_options={"values": ["Admin", "Editor", "Viewer"]}),
       ],
   )

Editor types
~~~~~~~~~~~~

The ``editor=`` argument on :class:`FieldItem <bootstack.widgets.form.FieldItem>`
forces a specific widget regardless of the field's value type. Editor names match
the corresponding ``bs.*`` widget class name in lowercase:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Editor
     - Public widget
     - Notes
   * - ``'textfield'``
     - :class:`TextField <bootstack.widgets.textfield.TextField>`
     - Single-line text input. Default for ``str``.
   * - ``'numberfield'``
     - :class:`NumberField <bootstack.widgets.numberfield.NumberField>`
     - Numeric input with stepper buttons. Default for ``int`` / ``float``.
   * - ``'passwordfield'``
     - :class:`PasswordField <bootstack.widgets.passwordfield.PasswordField>`
     - Masked text input. Default for ``dtype='password'``.
   * - ``'datefield'``
     - :class:`DateField <bootstack.widgets.datefield.DateField>`
     - Date picker with calendar popup. Default for ``date`` / ``datetime``.
   * - ``'textarea'``
     - :class:`TextArea <bootstack.widgets.textarea.TextArea>`
     - Multi-line text editor.
   * - ``'select'``
     - :class:`Select <bootstack.widgets.select.Select>`
     - Drop-down list. Requires ``editor_options={"values": [...]}``.
       Pass ``editor_options={"allow_custom_values": True}`` for an editable combobox.
   * - ``'spinnerfield'``
     - :class:`SpinnerField <bootstack.widgets.spinnerfield.SpinnerField>`
     - Numeric spinner field.
   * - ``'checkbox'``
     - :class:`Checkbox <bootstack.widgets.boolean_controls.Checkbox>`
     - Checkbox control. Default for ``bool``.
   * - ``'switch'``
     - :class:`Switch <bootstack.widgets.boolean_controls.Switch>`
     - Toggle switch.
   * - ``'slider'``
     - :class:`Slider <bootstack.widgets.slider.Slider>`
     - Horizontal slider.

Grouped fields
~~~~~~~~~~~~~~

Use :class:`GroupItem <bootstack.widgets.form.GroupItem>` to create a labeled
section with its own column layout:

.. code-block:: python

   bs.Form(
       items=[
           bs.GroupItem(
               label="Personal Info",
               col_count=2,
               items=[
                   bs.FieldItem(key="first_name", label="First Name"),
                   bs.FieldItem(key="last_name",  label="Last Name"),
                   bs.FieldItem(key="email",      label="Email"),
                   bs.FieldItem(key="phone",      label="Phone"),
               ],
           ),
       ],
   )

Groups can be nested and placed in specific grid cells using ``column=``,
``row=``, and ``columnspan=``.

Tabbed layouts
~~~~~~~~~~~~~~

Use :class:`TabsItem <bootstack.widgets.form.TabsItem>` with
:class:`TabItem <bootstack.widgets.form.TabItem>` to organize fields into tabs:

.. code-block:: python

   bs.Form(
       items=[
           bs.TabsItem(tabs=[
               bs.TabItem(
                   label="Account",
                   items=[
                       bs.FieldItem(key="username", label="Username"),
                       bs.FieldItem(key="password", label="Password", dtype="password"),
                   ],
               ),
               bs.TabItem(
                   label="Profile",
                   items=[
                       bs.FieldItem(key="bio",     label="Bio",     editor="textarea"),
                       bs.FieldItem(key="website", label="Website"),
                   ],
               ),
           ]),
       ],
   )

Validation
~~~~~~~~~~

Call ``validate()`` to run validation rules on all fields. Access individual
field widgets via ``field(key)`` to attach rules:

.. code-block:: python

   from bootstack.validation import ValidationRule

   form = bs.Form(data={"email": "", "username": ""})

   form.field("email").add_validation_rule(
       ValidationRule("email", message="Enter a valid email address.", trigger="blur")
   )
   form.field("username").add_validation_rule(
       ValidationRule("stringLength", min=3, message="At least 3 characters.", trigger="blur")
   )

   if form.validate():
       submit(form.value)

Reactive updates
~~~~~~~~~~~~~~~~

Use ``on_data_change=`` at construction time, or call ``on_data_change()``
after construction. Both receive the current form data as a dict:

.. code-block:: python

   # constructor kwarg
   bs.Form(
       data={"title": "", "description": ""},
       on_data_change=lambda data: preview(data),
   )

   # event shorthand — returns a Subscription
   form = bs.Form(data={"title": "", "description": ""})
   form.on_data_change(lambda data: preview(data))

   # composable Stream
   form.on_data_change().debounce(300).listen(lambda data: preview(data))

Footer buttons
~~~~~~~~~~~~~~

Pass ``buttons=`` to add a button row below the fields. Each button can be a
plain string, a ``DialogButton`` instance, or a dict with ``text``, ``role``,
and ``result`` keys. When clicked, ``form.result`` is set to that button's
``result`` value:

.. code-block:: python

   form = bs.Form(
       data={"name": "", "email": ""},
       buttons=[
           {"text": "Save",   "role": "primary", "result": "save"},
           {"text": "Cancel", "role": "cancel",  "result": None},
       ],
   )

   # after the user clicks:
   if form.result == "save":
       submit(form.value)

Button ``role`` controls the visual style: ``'primary'``, ``'secondary'``,
``'danger'``, or ``'cancel'``.

.. note::

   ``FormDialog`` uses this same mechanism internally — it wraps an embedded
   ``Form`` in a dialog window. Use ``buttons=`` on a standalone ``Form``
   when you want an in-page form with its own action row rather than a
   modal popup.

Reading and writing values
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   form = bs.Form(data={"name": "Alice", "age": 30})

   # Read all values
   values = form.value        # {'name': 'Alice', 'age': 30}
   values = form.get()        # equivalent

   # Write all values
   form.value = {"name": "Bob", "age": 25}
   form.set({"name": "Bob", "age": 25})   # equivalent

   # Read / write a single field
   name = form.get_field_value("name")
   form.set_field_value("name", "Carol")

   # Reactive access
   sig = form.field_signal("age")
   sig.subscribe(lambda v: print(f"age changed: {v}"))

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

:doc:`formdialog` — ``FormDialog`` embeds a ``Form`` in a dialog window with
built-in OK / Cancel buttons.

API
---

.. autoclass:: bootstack.widgets.form.Form
   :members:

FieldItem
~~~~~~~~~

.. class:: bootstack.widgets.form.FieldItem(key, label=None, dtype=None, readonly=False, visible=True, column=None, row=None, columnspan=1, rowspan=1, editor=None, editor_options=...)

   Field definition for use in ``Form(items=[...])``.

   :param key: Unique field identifier. Used to read and write the field value.
   :param label: Display label shown above the field. Defaults to the
       capitalized key when ``None``.
   :param dtype: Type hint controlling the default editor. One of
       ``'str'``, ``'int'``, ``'float'``, ``'bool'``, ``'date'``,
       ``'datetime'``, ``'password'``. ``None`` infers the type from the
       initial value.
   :param readonly: When ``True``, the field is rendered as read-only.
       Default ``False``.
   :param visible: When ``False``, the field is hidden. Default ``True``.
   :param column: Zero-based grid column. Auto-placed when ``None``.
   :param row: Zero-based grid row. Auto-placed when ``None``.
   :param columnspan: Number of grid columns to span. Default ``1``.
   :param rowspan: Number of grid rows to span. Default ``1``.
   :param editor: Force a specific editor widget. One of ``'textfield'``,
       ``'numberfield'``, ``'passwordfield'``, ``'datefield'``, ``'textarea'``,
       ``'select'``, ``'spinnerfield'``, ``'checkbox'``, ``'switch'``,
       ``'slider'``. See *Editor types* above for details.
   :param editor_options: Extra keyword arguments forwarded to the editor
       widget constructor. For ``'select'``, pass ``{"values": ["A", "B", "C"]}``.
       Pass ``{"allow_custom_values": True}`` for editable combobox behavior.

GroupItem
~~~~~~~~~

.. class:: bootstack.widgets.form.GroupItem(items, label=None, col_count=1, min_col_width=..., width=None, height=None, column=None, row=None, columnspan=1, rowspan=1, padding=8)

   Labeled group of fields with its own column layout.

   :param items: Child :class:`FieldItem`, :class:`GroupItem`, or
       :class:`TabsItem` instances (or equivalent dicts).
   :param label: Section heading shown above the group border. No border is
       drawn when ``None``.
   :param col_count: Number of columns within the group. Default ``1``.
   :param min_col_width: Minimum column width in pixels.
   :param width: Fixed width for the group container.
   :param height: Fixed height for the group container.
   :param column: Zero-based grid column in the parent form. Auto-placed when ``None``.
   :param row: Zero-based grid row in the parent form. Auto-placed when ``None``.
   :param columnspan: Columns to span in the parent grid. Default ``1``.
   :param rowspan: Rows to span in the parent grid. Default ``1``.
   :param padding: Internal padding inside the group border. Default ``8``.

TabsItem
~~~~~~~~

.. class:: bootstack.widgets.form.TabsItem(tabs, label=None, width=None, height=None, column=None, row=None, columnspan=1, rowspan=1)

   Tab container holding one or more :class:`TabItem` entries.

   :param tabs: :class:`TabItem` instances (or equivalent dicts) defining
       each tab.
   :param label: Optional heading shown above the tab bar.
   :param width: Fixed width for the tab container.
   :param height: Fixed height for the tab container.
   :param column: Zero-based grid column in the parent form. Auto-placed when ``None``.
   :param row: Zero-based grid row in the parent form. Auto-placed when ``None``.
   :param columnspan: Columns to span in the parent grid. Default ``1``.
   :param rowspan: Rows to span in the parent grid. Default ``1``.

TabItem
~~~~~~~

.. class:: bootstack.widgets.form.TabItem(label, items, padding=8)

   Single tab within a :class:`TabsItem`.

   :param label: Tab button label.
   :param items: :class:`FieldItem`, :class:`GroupItem`, or
       :class:`TabsItem` instances for this tab's content.
   :param padding: Internal padding inside the tab body. Default ``8``.

Full Example
------------

.. literalinclude:: ../../docs/examples/forms.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs