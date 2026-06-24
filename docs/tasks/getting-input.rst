Getting Input
=============

bootstack has a field widget for every common kind of value — text, numbers,
dates, choices, on/off flags. They all share one idea: a field holds a **value**
you can read at any time, and you can **bind** that value to a :class:`Signal
<bootstack.Signal>` so it stays in sync with the rest of your app without manual
callbacks.

This guide covers reading and binding values. To check what the user typed, see
:doc:`/reference/validation`; to react to changes as they happen, see
:doc:`handling-actions`.

Text
----

:class:`~bootstack.TextField` is the single-line text input. Read the current
string from `.value`; seed it with a positional argument and add a
`placeholder=` for the empty hint:

.. code-block:: python

   name = bs.TextField("Ada", placeholder="Your name", label="Name")
   print(name.value)        # "Ada"

For longer text use :class:`~bootstack.TextArea`, for hidden entry
:class:`~bootstack.PasswordField` (with a built-in show/hide toggle), and for
source or config text :class:`~bootstack.CodeEditor`. All three expose the same
`.value` string.

Numbers
-------

:class:`~bootstack.NumberField` parses what the user types into an `int` or
`float`, clamps it to `min_value` / `max_value`, and steps by `step` with its
+/− buttons. `.value` is the parsed number (or `None` when the field is empty):

.. code-block:: python

   qty = bs.NumberField(value=1, min_value=1, max_value=99, step=1, label="Quantity")
   price = bs.NumberField(value=9.99, min_value=0, step=0.5, label="Price")

Use an integer `value`/`step` for whole numbers and a float for fractional ones —
the field follows the type you give it.

Dates and times
---------------

:class:`~bootstack.DateField` and :class:`~bootstack.TimeField` return real
`datetime.date` and `datetime.time` objects from `.value`, never strings. A date
field carries a calendar popup; a time field offers a dropdown of times. Both
accept constraints:

.. code-block:: python

   from datetime import date

   when = bs.DateField(value=date.today(), min_date=date.today(), label="Ship date")
   at = bs.TimeField(value=None, interval=15, label="Reminder")

   print(when.value)        # datetime.date(2026, 6, 14)

Choices
-------

For a single choice from a list, the widget depends on how much room you have and
how many options there are:

- :class:`~bootstack.RadioGroup` — a few options, all visible at once.
- :class:`~bootstack.Select` — a dropdown; `searchable=True` filters as you type.
- :class:`~bootstack.SelectButton` — a compact button that opens a menu.

Options can be plain strings, or `(label, value)` tuples when the text shown
differs from the value you store. `.value` is always the value; `.text` is the
visible label:

.. code-block:: python

   size = bs.RadioGroup(["Small", "Medium", "Large"], value="Medium", title="Size")

   theme = bs.Select(
       options=[("Light theme", "light"), ("Dark theme", "dark")],
       value="light",
       label="Theme",
   )
   print(theme.value, theme.text)   # "light" "Light theme"

For multiple choices, use :class:`~bootstack.ToggleGroup` with `mode="multi"`
(its `.value` is a `set`), or a column of :class:`~bootstack.Checkbox` widgets.

Sliders
-------

:class:`~bootstack.Slider` picks a number on a track — handy when the rough
magnitude matters more than an exact figure. :class:`~bootstack.RangeSlider`
picks a low/high pair:

.. code-block:: python

   volume = bs.Slider(value=50, min_value=0, max_value=100, show_value=True)
   price_range = bs.RangeSlider(low_value=20, high_value=80, min_value=0, max_value=100)

   print(volume.value)              # 50.0
   print(price_range.value)         # (20.0, 80.0)

On/off
------

:class:`~bootstack.Checkbox` and :class:`~bootstack.Switch` are boolean controls —
`.value` is `True` or `False`. A `Switch` reads as an immediate setting (Wi-Fi
on/off); a `Checkbox` reads as a selection you confirm later (terms accepted).
:class:`~bootstack.ToggleButton` is the same idea styled as a pressable button.

.. code-block:: python

   notify = bs.Switch("Email notifications", value=True)
   agree = bs.Checkbox("I accept the terms")

Binding values with signals
---------------------------

Reading `.value` on demand is fine for a submit button. But when the same value
drives several widgets — a live preview, a summary label, a dependent control —
bind it to a :class:`~bootstack.Signal` instead. Every widget bound to the same
signal updates together, in both directions.

Text-bearing fields use `textsignal=`; everything with a typed value uses
`signal=`:

.. code-block:: python

   with bs.App(title="Live preview", padding=16, gap=8) as app:
       name = bs.Signal("World")
       bs.TextField(textsignal=name, placeholder="Type a name…")
       bs.Label(textsignal=name, font="heading-md", accent="primary")

   app.run()

`NumberField`, `DateField`, and `TimeField` bind their **typed** value through
`signal=` — the signal holds an `int`/`float`, a `date`, or a `time`, not the
formatted text:

.. code-block:: python

   from datetime import date

   count = bs.Signal(0)
   bs.NumberField(signal=count, min_value=0)
   bs.Label(textsignal=count.map(lambda n: f"{n} items"))   # derived label

   day = bs.Signal(date.today())
   bs.DateField(signal=day)

Boolean and choice controls bind through `signal=` as well — a `Checkbox` to a
`Signal(bool)`, a `RadioGroup` to a `Signal` holding the selected value. See
:doc:`/reference/signals` for deriving and combining signals.

.. note::

   When you pass both `signal=` and an initial `value=` to a boolean control,
   the signal wins — seed the value on the signal itself
   (`bs.Signal(True)`), not on the widget.

See also
--------

- :doc:`customizing-fields` — add icons, buttons, and toggles inside a field.
- :doc:`/reference/signals` — binding, deriving, and combining reactive values.
- :doc:`/reference/validation` — checking input against rules.
- :doc:`handling-actions` — reacting to changes and clicks.
- :doc:`building-forms` — collecting many fields at once.
