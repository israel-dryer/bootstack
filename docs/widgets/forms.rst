.. _forms:

Form
====

``bs.Form`` builds a data-entry layout from a dict or an explicit list of field
definitions. Fields are placed on a grid; :class:`GroupItem
<bootstack.widgets.form.GroupItem>` creates labeled sections and
:class:`TabsItem <bootstack.widgets.form.TabsItem>` creates a tabbed layout.

.. image:: /_static/examples/forms-hero-light.png
   :class: bs-screenshot-light
   :alt: Form demo — light theme

.. image:: /_static/examples/forms-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Form demo — dark theme

Usage
-----

A ``Form`` turns a dict (or a list of field definitions) into a laid-out,
validating data-entry surface — fields map to the right widget by value type,
``form.values`` reads them all back, and ``form.valid`` tracks validity
reactively. Embed it in a page, or use a :doc:`FormDialog <formdialog>` for a
modal.

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
           "street": "123 Main St",
           "city": "Springfield",
           "state": "IL",
           "zip": "62701",
       },
       col_count=2,
   )

.. image:: /_static/examples/forms-columns-light.png
   :class: bs-screenshot-light
   :alt: Form multiple columns — light theme

.. image:: /_static/examples/forms-columns-dark.png
   :class: bs-screenshot-dark
   :alt: Form multiple columns — dark theme

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

Editor options
~~~~~~~~~~~~~~

``editor_options`` are the keyword arguments of the editor's public widget — the
same names you would pass when constructing that ``bs.*`` widget directly. For a
``numberfield`` that means :class:`NumberField <bootstack.widgets.numberfield.NumberField>`
options such as ``step`` and ``min_value``; for a ``textarea`` it means
:class:`TextArea <bootstack.widgets.textarea.TextArea>` options such as ``show_border``:

.. code-block:: python

   bs.Form(
       items=[
           bs.FieldItem(key="quantity", label="Quantity", editor="numberfield",
                        editor_options={"step": 10, "min_value": 0}),
           bs.FieldItem(key="notes", label="Notes", editor="textarea",
                        editor_options={"height": 5, "show_border": True}),
       ],
   )

An option that names something the form also fills — such as ``label``, or a
select's choices — overrides the form's own default. Two behave differently:
``value`` seeds the editor only when the form's ``data`` carries nothing for
that key, so your record always wins; and ``parent`` is owned by the form,
which places every editor in its own field container.

Grouped fields
~~~~~~~~~~~~~~

Use :class:`GroupItem <bootstack.widgets.form.GroupItem>` to create a labeled
section with its own column layout:

.. code-block:: python

   bs.Form(
       items=[
           bs.GroupItem(
               label="Contact",
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

.. image:: /_static/examples/forms-grouped-light.png
   :class: bs-screenshot-light
   :alt: Form grouped fields — light theme

.. image:: /_static/examples/forms-grouped-dark.png
   :class: bs-screenshot-dark
   :alt: Form grouped fields — dark theme

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

.. image:: /_static/examples/forms-tabbed-light.png
   :class: bs-screenshot-light
   :alt: Form tabbed layout — light theme

.. image:: /_static/examples/forms-tabbed-dark.png
   :class: bs-screenshot-dark
   :alt: Form tabbed layout — dark theme

Validation
~~~~~~~~~~

Call ``validate()`` to run validation rules on all fields. Access individual
field widgets via ``field(key)`` to attach rules:

.. code-block:: python

   form = bs.Form(data={"email": "", "username": ""})

   form.field("email").add_validation_rule(
       "email", message="Enter a valid email address.", trigger="blur"
   )
   form.field("username").add_validation_rule(
       "stringLength", min=3, message="At least 3 characters.", trigger="blur"
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
``'danger'``, or ``'cancel'``. A plain string button carries no role, so it
renders in the neutral default style regardless of its position in the row — give
a button a ``role`` (through a dict or ``DialogButton``) to make it primary or
destructive.

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

The complete reference for :class:`Form <bootstack.Form>` and its item types —
``FieldItem``, ``GroupItem``, ``TabsItem``, ``TabItem``, and the ``FormItem``
union — lives on the :doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Form
   ~bootstack.FieldItem
   ~bootstack.GroupItem
   ~bootstack.TabsItem
   ~bootstack.TabItem
   ~bootstack.FormItem

Full Example
------------

.. literalinclude:: ../../docs/examples/forms.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs