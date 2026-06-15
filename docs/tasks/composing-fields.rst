Composing Custom Fields
=======================

Every bootstack field — :class:`~bootstack.TextField`,
:class:`~bootstack.NumberField`, :class:`~bootstack.DateField`, and the rest —
can carry small **addons** inside its border: an icon, a label, a button, or an
on/off toggle, sitting before or after the input. Addons are how you turn a plain
field into a purpose-built one — a search box, a price input, a copyable key —
without writing a new widget class.

This guide builds those fields by composition. To read and bind a field's value,
see :doc:`getting-input`; to arrange and validate several fields together, see
:doc:`building-forms`.

The addon model
---------------

Add an addon by calling `insert_addon(kind, position)` on any field. There are
three kinds and two positions:

- **kind** — `'button'` (clickable), `'label'` (static text or icon), or
  `'toggle'` (an on/off control).
- **position** — `'before'` (left of the input) or `'after'` (right of it).

An addon is a real widget, not a decoration. You give it `text` or an `icon` to
show and an `accent` for color; a button or toggle also takes an `on_click`
handler. Pass a `name` to keep a handle on it — named addons can be restyled or
removed later. The recipes below introduce each option where it earns its keep.

Labels: icons and affixes
-------------------------

The simplest addon is a `label` — static text or an icon that describes the field
without reacting to anything. *Affixes* are the everyday case: a symbol on each
side that says what a bare value means. Frame a :class:`~bootstack.NumberField`
with a currency symbol before the number and a unit after it, and `1499` reads as
a price:

.. code-block:: python

   price = bs.NumberField(value=1499, label="Price", fill="x")
   price.insert_addon("label", "before", text="$")
   price.insert_addon("label", "after", text="USD", accent="secondary")

The trailing unit takes a muted `accent` so it stays subordinate — the value, not
the label, is what the eye should land on first.

.. image:: /_static/examples/composing-fields-amount-light.png
   :class: bs-screenshot-light
   :alt: Number field with a dollar-sign prefix and a USD suffix label — light theme

.. image:: /_static/examples/composing-fields-amount-dark.png
   :class: bs-screenshot-dark
   :alt: Number field with a dollar-sign prefix and a USD suffix label — dark theme

An icon label does the same job with fewer words. Dropped in front of a
:class:`~bootstack.DateField`, a `cake` glyph reads as *birthday* on sight,
sparing you a longer caption. The call is the same on any field, text or not:

.. code-block:: python

   import datetime

   bday = bs.DateField(label="Date of birth", value=datetime.date(1990, 5, 4), fill="x")
   bday.insert_addon("label", "before", icon="cake")

.. image:: /_static/examples/composing-fields-birthday-light.png
   :class: bs-screenshot-light
   :alt: Date field with a leading cake icon — light theme

.. image:: /_static/examples/composing-fields-birthday-dark.png
   :class: bs-screenshot-dark
   :alt: Date field with a leading cake icon — dark theme

Buttons: acting on the value
----------------------------

A `button` addon runs an `on_click` handler — usually something that touches the
field's value. A search box is the familiar shape: a magnifying-glass label on
the left for recognition, and a clear button on the right that empties the field:

.. code-block:: python

   field = bs.TextField(placeholder="Search products...", fill="x")
   field.insert_addon("label", "before", icon="search")

   def clear():
       field.value = ""

   field.insert_addon("button", "after", name="clear", icon="x-lg", on_click=clear)

Only the `button` carries the handler; the leading icon is an inert `label`.
Giving the button a `name` lets you reach it again later.

.. image:: /_static/examples/composing-fields-search-light.png
   :class: bs-screenshot-light
   :alt: Search field with a leading search icon and a trailing clear button — light theme

.. image:: /_static/examples/composing-fields-search-dark.png
   :class: bs-screenshot-dark
   :alt: Search field with a leading search icon and a trailing clear button — dark theme

A button that *changes* the value, though, has no business working on a read-only
field — and by default it won't. An addon follows its field's read-only state and
dims along with it, which is exactly right for a clear button or the number spin
buttons. A button that only *reads* the value is the exception: this copy button
writes the field to the clipboard, so it opts back in with
`active_when_readonly=True`:

.. code-block:: python

   key = bs.TextField(value="sk-live-7f3a9c2b", label="API key", read_only=True, fill="x")

   def do_copy():
       key.set_clipboard(key.value)

   key.insert_addon("button", "after", name="copy", icon="clipboard",
                    on_click=do_copy, active_when_readonly=True)

A fully `disabled` field still dims every addon, the opt-in ones included —
disabled means inert, no exceptions.

.. image:: /_static/examples/composing-fields-copy-light.png
   :class: bs-screenshot-light
   :alt: Read-only API key field with a trailing copy button — light theme

.. image:: /_static/examples/composing-fields-copy-dark.png
   :class: bs-screenshot-dark
   :alt: Read-only API key field with a trailing copy button — dark theme

Toggles: state you can read
---------------------------

A `toggle` addon holds an on/off state instead of firing once. Bind it to a
:class:`~bootstack.Signal` and that state becomes readable from anywhere in your
app — here, whether a width is measured in pixels or percent:

.. code-block:: python

   size = bs.NumberField(value=64, label="Width", fill="x")
   percent = bs.Signal(False)        # False -> px, True -> %
   size.insert_addon("toggle", "after", name="unit", text="px", signal=percent)

   def show_unit(is_percent):
       size.update_addon("unit", text="%" if is_percent else "px")

   percent.subscribe(show_unit)

The Signal is the source of truth: the toggle flips it, and the subscriber
relabels the addon through `update_addon` so the button always shows the current
unit. Anywhere else in your code, `percent()` tells you which unit to apply.

.. image:: /_static/examples/composing-fields-unit-light.png
   :class: bs-screenshot-light
   :alt: Number field with a trailing unit toggle showing percent — light theme

.. image:: /_static/examples/composing-fields-unit-dark.png
   :class: bs-screenshot-dark
   :alt: Number field with a trailing unit toggle showing percent — dark theme

Managing addons
---------------

A named addon stays reachable after the field is built, so you can restyle or
drop it as your state changes:

.. code-block:: python

   field.update_addon("clear", icon="trash", accent="danger")
   field.remove_addon("clear")
   field.addons               # the live addon widgets, keyed by name

`update_addon` changes only the options you pass and leaves the rest in place;
`remove_addon` detaches and destroys the addon. Reach for the `addons` mapping
when you need a widget directly.

Reusable fields
---------------

bootstack has no public base class for authoring an entirely new field *type* —
but you rarely need one. A configured field is an ordinary object, so the
practical way to ship a custom input is to wrap a recipe in a function:

.. code-block:: python

   def search_field(**kwargs):
       field = bs.TextField(**kwargs)
       field.insert_addon("label", "before", icon="search")

       def clear():
           field.value = ""

       field.insert_addon("button", "after", name="clear", icon="x-lg", on_click=clear)
       return field

   # use it like any other field
   with bs.VStack(gap=8):
       query = search_field(placeholder="Search...", fill="x")
       bs.Button("Go", on_click=lambda: run_query(query.value))

`search_field()` returns a real :class:`~bootstack.TextField`, so `.value`,
validation, and signal binding all work on it exactly as they would on a plain
field. Call it wherever you would build one.

See also
--------

- :doc:`getting-input` — reading and binding a field's value.
- :doc:`building-forms` — laying out and validating groups of fields.
- :doc:`/reference/validation` — validation rules for field input.
