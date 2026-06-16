Handling Actions
================

An *action* is anything the user does that your app responds to — clicking a
button, changing a field, pressing a shortcut, choosing a menu item. bootstack
gives you a single, consistent way to wire all of them: pass a handler now, or
subscribe to an event stream you can shape.

Button clicks
-------------

The shortest path is the `on_click=` argument. It takes a plain no-argument
callable — run when the button is pressed:

.. code-block:: python

   bs.Button("Save", accent="primary", on_click=save_document)
   bs.Button("Cancel", variant="ghost", on_click=lambda: app.close())

That covers the vast majority of buttons. When you need the *details* of the
click — the pointer position, or which modifier keys were held — call the
`on_click()` **method** instead. It hands your handler an :class:`Event
<bootstack.events.Event>` carrying the pointer coordinates (`x`, `y`) and the
modifier flags (`ctrl`, `shift`, `alt`, `meta`):

.. code-block:: python

   row = bs.Button("Open")
   row.on_click(lambda e: open_in_new_tab() if e.ctrl else open_here())

Both reach the same click. Use the argument for a simple action, and the method
when you need the event object.

Reacting to value changes
-------------------------

Every field exposes `on_*()` event shorthands. The most common is `on_change`,
which fires when a value is committed (on blur or Enter). The handler receives a
typed payload — for a value change that is a :class:`ChangeEvent
<bootstack.events.ChangeEvent>` carrying `.value` and `.prev_value`:

.. code-block:: python

   qty = bs.NumberField(value=1, min_value=1)
   qty.on_change(lambda e: print(f"changed from {e.prev_value} to {e.value}"))

Each event delivers the payload that fits it:

- `on_input` fires on every keystroke and carries the live `.text`.
- A :class:`~bootstack.Slider` `on_change` carries the slider's `.value`.
- Selection widgets carry the selected record.
- Native events — `on_click`, `on_hover`, `on_focus`, `on_blur` — carry the
  general-purpose `Event` (pointer position and modifier keys) instead of a
  typed payload.

The :doc:`/reference/events` guide maps every event to its payload.

`on_change(handler)` returns a :class:`Subscription
<bootstack.events.Subscription>`. Hold onto it to stop listening later with
`subscription.cancel()`.

Shaping events with streams
---------------------------

Call an `on_*()` shorthand **without** a handler and you get a composable
:class:`Stream <bootstack.streams.Stream>` instead of subscribing immediately.
Streams let you transform the event flow before it reaches your handler — the
classic case is debouncing a search box so it only queries once the user pauses:

.. code-block:: python

   search = bs.TextField(placeholder="Search…")

   (search.on_input()
       .debounce(300)
       .filter(lambda e: len(e.text) >= 2)
       .listen(lambda e: run_search(e.text)))

Streams offer `map`, `filter`, `debounce`, `throttle`, `delay`, and `tap`;
`listen()` is the terminal step that activates the binding and returns a
cancellable handle. See :doc:`/reference/streams`.

Keyboard shortcuts
------------------

Register app-wide shortcuts through the :mod:`bootstack.shortcuts` service. Use
the `Mod` token for the platform's primary modifier — it maps to Ctrl on
Windows/Linux and ⌘ on macOS — and bind the service to your window once:

.. code-block:: python

   from bootstack.shortcuts import get_shortcuts

   shortcuts = get_shortcuts()
   shortcuts.register("save", "Mod+S", save_document)
   shortcuts.register("find", "Mod+F", open_search)
   shortcuts.bind_to(app)

See :doc:`/reference/shortcuts` for the full lifecycle (display labels,
unregistering, listing).

Menus and toolbars
------------------

`App`, `AppShell`, and `Window` all carry a top region of stacked toolbars, added
with `add_toolbar()`. A toolbar holds buttons and **menus** alike — a menu action
takes the same `on_click=` callable as a button, and a `shortcut=` that is
**both** displayed beside the item **and** bound for you:

.. code-block:: python

   with app.add_toolbar() as bar:
       with bar.add_menu("File") as file:
           file.add_action("Save", shortcut="Mod+S", on_click=save_document)
           file.add_action("Open…", shortcut="Mod+O", on_click=open_document)
           file.add_separator()
           file.add_action("Quit", shortcut="Mod+Q", on_click=app.close)
       bar.add_button("Save", icon="save", on_click=save_document)
       bar.add_spacer()
       bar.add_button("Settings", icon="gear", on_click=open_settings)

See also
--------

- :doc:`/reference/events` — every event, its payload, and the `on_*` model.
- :doc:`/reference/streams` — composing and transforming event streams.
- :doc:`/reference/shortcuts` — the keyboard-shortcut service.
- :doc:`getting-input` — the fields whose changes you are handling here.
