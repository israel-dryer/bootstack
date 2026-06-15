Events
======

Widgets announce what they do as named events — a button reports a ``click``,
a field reports a ``change`` when its value is committed. You respond by binding
a handler. Each widget exposes ``on_*()`` shorthands for the events it supports,
and every handler can be detached again through the subscription it returns.

What a handler receives
-----------------------

There are two kinds of event, and the handler argument differs accordingly:

- **Data-carrying events** (``change``, ``input``, ``select``, …) hand the
  handler a typed *payload* object directly — the argument **is** the payload.
  Read its attributes straight off: ``e.value``, ``e.text``, ``e.record``.
- **Native events** (``click``, ``hover``, ``focus``, ``blur``, ``resize``,
  key and scroll events) carry no payload, so the handler receives a curated
  :class:`Event <bootstack.events.Event>` describing where it happened and which
  modifier keys were held.

Every payload type is cataloged in :mod:`bootstack.events`, so editors can
autocomplete the attributes available on each event.

.. note::

   Two widgets hand their handlers a plain object instead of a payload
   dataclass, by design. :class:`~bootstack.ListView` item events
   (``on_item_click``, ``on_item_insert``, …) and :class:`~bootstack.Form`'s
   ``on_data_change`` deliver the **record dict** directly (``e["field"]``).
   :class:`~bootstack.Tree` node events (``on_activate``, ``on_expand``,
   ``on_collapse``) deliver the ``TreeNode`` handle. Everywhere else, a
   data-carrying event is one of the payloads below.

Listening for an event
----------------------

Call the matching ``on_*()`` shorthand with a handler. It binds immediately and
returns a :class:`Subscription <bootstack.events.Subscription>`:

.. code-block:: python

   field = bs.TextField()

   field.on_change(lambda e: print("committed:", e.value))
   field.on_input(lambda e: print("typed:", e.text))

For a simple button action, the ``on_click=`` constructor argument takes a
**no-argument** callback:

.. code-block:: python

   bs.Button("Save", on_click=lambda: save())

Every shorthand is a thin wrapper over the generic ``on()`` method, which takes
the event name as a string. Reach for it for an event without a dedicated
shorthand, or when the event name is computed:

.. code-block:: python

   widget.on("right_click", show_context_menu)

The shorthand and the generic form are the same call: for an event named
``change``, ``widget.on_change(handler)`` is shorthand for
``widget.on("change", handler)``. The tables below name each event, so you can
use either form.

Events by widget
----------------

Each widget exposes only the events that make sense for it. This is the map from
a widget to the events you can bind and the payload each one delivers — reach for
it when you know the widget but not the event name. (The
:doc:`API reference </api-reference/events>` is the complementary index,
organized by payload type.)

**Actions**

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Widget
     - Event
     - Handler receives
   * - :class:`~bootstack.Button`, :class:`~bootstack.Label`
     - ``click``
     - :class:`~bootstack.events.Event` (native)
   * - :class:`~bootstack.ButtonGroup`
     - ``click``
     - :class:`~bootstack.events.ButtonGroupClickEvent`
   * - :class:`~bootstack.MenuButton`, :class:`~bootstack.ContextMenu`
     - ``select``
     - :class:`~bootstack.events.MenuSelectEvent`

**Text, number, and date fields** (TextField, NumberField, PathField,
PasswordField, DateField, TimeField, SpinnerField) share one event set —
``on_input`` fires on every keystroke, ``on_change`` when the value is committed
(blur or Enter), and ``on_submit`` on Enter.

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Widget
     - Event
     - Handler receives
   * - Any field
     - ``input``
     - :class:`~bootstack.events.InputEvent`
   * - (same)
     - ``change``
     - :class:`~bootstack.events.ChangeEvent`
   * - (same)
     - ``submit``
     - :class:`~bootstack.events.Event`
   * - (same)
     - ``valid`` / ``invalid`` / ``validate``
     - :class:`~bootstack.events.ValidationEvent`
   * - (same)
     - ``focus`` / ``blur``
     - :class:`~bootstack.events.Event`

**Boolean and selection controls**

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Widget
     - Event
     - Handler receives
   * - :class:`~bootstack.Checkbox`, :class:`~bootstack.Switch`,
       :class:`~bootstack.ToggleButton`
     - ``change``
     - :class:`~bootstack.events.ChangeEvent`
   * - (same)
     - ``check`` / ``uncheck``
     - :class:`~bootstack.events.Event` (data-free)
   * - :class:`~bootstack.Select`, :class:`~bootstack.SelectButton`,
       :class:`~bootstack.RadioGroup`, :class:`~bootstack.ToggleGroup`
     - ``change``
     - :class:`~bootstack.events.ChangeEvent`

**Sliders and meters**

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Widget
     - Event
     - Handler receives
   * - :class:`~bootstack.Slider`, :class:`~bootstack.Gauge`
     - ``change``
     - :class:`~bootstack.events.SliderEvent`
   * - :class:`~bootstack.Slider`
     - ``commit``
     - :class:`~bootstack.events.SliderCommitEvent`
   * - :class:`~bootstack.RangeSlider`
     - ``change`` / ``commit``
     - :class:`~bootstack.events.RangeSliderEvent` /
       :class:`~bootstack.events.RangeSliderCommitEvent`
   * - :class:`~bootstack.Calendar`
     - ``select``
     - :class:`~bootstack.events.DateSelectEvent`

**Lists, tables, and trees**

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Widget
     - Event
     - Handler receives
   * - :class:`~bootstack.ListView`
     - ``item_click``, ``item_insert``, ``item_update``,
       ``item_delete``
     - the record ``dict``
   * - :class:`~bootstack.DataTable`
     - ``row_click``, ``row_double_click``, ``row_right_click``
     - :class:`~bootstack.events.RowEvent`
   * - :class:`~bootstack.DataTable`
     - ``select``
     - :class:`~bootstack.events.SelectionEvent`
   * - :class:`~bootstack.DataTable`
     - ``rows_insert``, ``rows_update``, ``rows_delete``,
       ``rows_move``
     - :class:`~bootstack.events.RowsEvent`
   * - :class:`~bootstack.DataTable`
     - ``export``
     - :class:`~bootstack.events.ExportEvent`
   * - :class:`~bootstack.Tree`
     - ``select``
     - :class:`~bootstack.events.TreeSelectionEvent`
   * - :class:`~bootstack.Tree`
     - ``activate``, ``expand``, ``collapse``
     - the ``TreeNode`` handle

**Navigation and containers**

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Widget
     - Event
     - Handler receives
   * - :class:`~bootstack.Tabs`
     - ``change``
     - :class:`~bootstack.events.TabChangeEvent`
   * - :class:`~bootstack.Tabs`
     - ``tab_close``
     - :class:`~bootstack.events.TabCloseEvent`
   * - :class:`~bootstack.PageStack`, :class:`~bootstack.AppShell`
     - ``page_change``
     - :class:`~bootstack.events.PageChangeEvent`
   * - :class:`~bootstack.AppShell`
     - ``workspace_change``
     - :class:`~bootstack.events.WorkspaceChangeEvent`
   * - :class:`~bootstack.AppShell`
     - ``sidebar_toggle`` / ``sidebar_mode_change``
     - :class:`~bootstack.events.PaneToggleEvent` /
       :class:`~bootstack.events.DisplayModeEvent`
   * - :class:`~bootstack.Accordion`
     - ``change``
     - :class:`~bootstack.events.AccordionChangeEvent`

Each widget's own guide lists its complete event set; the tables above cover the
events you reach for most.

Reading a payload
-----------------

For a data-carrying event the handler argument is the payload itself. Read the
attributes straight off it — editors autocomplete them because every payload is
a frozen dataclass.

A ``change`` event is a :class:`~bootstack.events.ChangeEvent` carrying the
committed ``value``, the ``prev_value``, and the raw ``text``:

.. code-block:: python

   def on_change(e):
       print(e.value, "was", e.prev_value)

   field.on_change(on_change)

A **slider** distinguishes the value moving from the value settling. Use
``on_change`` for live feedback as the handle drags, and ``on_commit`` for the
expensive work you only want once the drag ends:

.. code-block:: python

   preview = bs.Label("100%")
   slider = bs.Slider(value=100, min_value=0, max_value=200)

   def show_zoom(e):
       preview.text = f"{e.value:.0f}%"

   slider.on_change(show_zoom)
   slider.on_commit(lambda e: apply_zoom(e.value))

A **table** reports both the row a user acts on and the current selection. A
:class:`~bootstack.events.RowEvent` carries the ``record`` and its ``id``; a
:class:`~bootstack.events.SelectionEvent` carries every selected ``record`` and
``id``:

.. code-block:: python

   def show_count(e):
       status.text = f"{len(e.records)} selected"

   table.on_row_double_click(lambda e: open_detail(e.id))
   table.on_select(show_count)

A **tab strip** tells you not just which tab is active but *why* it changed — a
:class:`~bootstack.events.TabChangeEvent` carries the ``current`` and
``previous`` tab (each a :class:`~bootstack.events.TabRef`), plus the ``reason``
and ``via`` tags. Use them to ignore programmatic changes, for example:

.. code-block:: python

   def on_tab(e):
       if e.reason == "user":
           track_view(e.current.key)

   tabs.on_change(on_tab)

A **page change** carries navigation context — a
:class:`~bootstack.events.PageChangeEvent` exposes the ``page`` now active, the
``prev_page``, and ``can_back`` / ``can_forward`` flags you can bind a toolbar
to:

.. code-block:: python

   def on_page(e):
       back_button.disabled = not e.can_back

   shell.on_page_change(on_page)

The curated Event
-----------------

Native events hand the handler a frozen :class:`Event
<bootstack.events.Event>`. It exposes the originating ``widget``, the pointer
position (``x``, ``y``, ``x_root``, ``y_root``), the widget ``width`` and
``height``, scroll ``delta``, modifier-key booleans (``ctrl``, ``shift``,
``alt``, ``meta``), and — for keyboard events — a clean ``key`` and ``char``.

.. code-block:: python

   button.on_click(lambda e: print("clicked at", e.x, e.y, "ctrl:", e.ctrl))

These pointer, focus, and geometry events can be bound on **any** widget by
name. Several have no ``on_*()`` shorthand, so ``on()`` is the only way to reach
them:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Event
     - Fires when
   * - ``click``, ``double_click``, ``right_click``
     - A mouse button is pressed over the widget.
   * - ``hover``, ``leave``
     - The pointer enters or leaves the widget.
   * - ``focus``, ``blur``
     - The widget gains or loses keyboard focus.
   * - ``resize``
     - The widget's size changes.

Each hands the handler a curated :class:`Event <bootstack.events.Event>`. Pass
any of these names to ``on()`` (``click``, ``focus``, and ``blur`` also have
shorthands on the widgets that emit them).

Widget lifecycle
----------------

Every widget also reports its own teardown. ``on_destroy`` fires once, as the
widget is being destroyed — when you call ``widget.destroy()``, when a container
it lives in is torn down (each child fires its own), or when the window closes.
It is the place to release anything the widget holds that is not cleaned up for
you: a file handle, an external subscription, a timer you started outside the
widget's own ``schedule`` (jobs on that are canceled automatically).

.. code-block:: python

   feed = open_price_feed()
   ticker = bs.Label("—")

   ticker.on_destroy(lambda e: feed.close())

The handler receives the same curated :class:`Event <bootstack.events.Event>` as
the native events above. Unlike them, ``on_destroy`` fires exactly once and
cannot be canceled. For a *window's* close button — which a handler can veto —
use ``on_close`` instead (see :doc:`/getting-started/app-structures`).

Detaching and reattaching
-------------------------

Destroying a widget is permanent. To pull a widget out of the layout *without*
tearing it down — and put it back later in the same spot — use ``detach`` and
``attach``. A detached widget stops taking up space but keeps its state,
children, and bindings.

.. code-block:: python

   panel = bs.VStack()
   ...
   panel.detach()            # hide it — frees its space
   panel.attach()            # bring it back exactly where it was

``attach`` accepts the same layout options as the constructor, so you can move a
widget as you bring it back. For stacked widgets, ``index=`` sets the position
among the currently attached siblings (or pass an explicit ``before=`` /
``after=`` sibling):

.. code-block:: python

   row.detach()
   row.attach(index=0)       # back at the top of its stack

The ``is_attached`` property reports the current state, and a plain ``detach()``
on an already-detached widget (or ``attach()`` after a no-argument ``detach``)
round-trips cleanly.

To build a widget that starts hidden, pass ``attached=False`` to its
constructor. It is created and parented in place — so a later ``attach()``
drops it into the slot it was declared in — but takes up no space until shown,
with no startup flicker:

.. code-block:: python

   with bs.VStack():
       bs.Label("Account")
       banner = bs.Label("Saved!", accent="success", attached=False)
       bs.TextField()

   ...
   banner.attach()           # reveal it between the label and the field

Two events bracket this. ``on_attach`` fires whenever the widget enters the
layout — on its initial placement and on every ``attach`` — and ``on_detach``
fires when it leaves, including when an ancestor hides it. They are the place to
start and stop work that should only run while the widget is on screen:

.. code-block:: python

   chart = bs.Card()
   chart.on_attach(lambda e: feed.subscribe(chart.refresh))
   chart.on_detach(lambda e: feed.unsubscribe(chart.refresh))

Each hands the handler a curated :class:`Event <bootstack.events.Event>`.

Filtering native events
-----------------------

The modifier state arrives as plain booleans, so branching on it is ordinary
Python. A Ctrl-click that means something different from a plain click:

.. code-block:: python

   def on_click(e):
       if e.ctrl:
           add_to_selection(e.widget)
       else:
           replace_selection(e.widget)

   row.on_click(on_click)

To filter *before* the handler runs — so the handler only sees the events you
care about — bind a :doc:`stream </reference/streams>` instead and chain
``filter``:

.. code-block:: python

   # Only Ctrl-clicks reach the handler.
   row.on_click().filter(lambda e: e.ctrl).listen(add_to_selection)

Subscriptions and stream handles
--------------------------------

Binding a handler directly returns a :class:`Subscription
<bootstack.events.Subscription>`; building a :doc:`stream </reference/streams>`
returns a ``Handle``. The two are interchangeable where it counts — both detach
the handler when you call ``cancel()``, and both work as context managers. Hold
on to whichever you get when the handler outlives the thing it watches:

.. code-block:: python

   sub = item.on_click(handle_select)
   sub.cancel()          # stop listening

A subscription (or handle) is also a context manager, which binds the handler
only for the duration of a block. Reach for this when a binding's life should
match a **bounded interaction that runs its own event loop** — most often a
modal dialog. While the dialog below is open, the table's selection is mirrored
into it; the handler is removed the moment the dialog closes, even on an error:

.. code-block:: python

   with table.on_select(lambda e: dialog.set_count(len(e.records))):
       dialog.show()     # modal — runs until the user closes it

Around ordinary synchronous code the event loop never pumps, so the handler
would never fire before the block exits — use ``with`` only when something
inside it processes events.

Emitting your own events
------------------------

Use ``emit()`` to fire an event yourself, optionally with a payload — this is how
a composite widget surfaces its own high-level activity to listeners. Any name
that isn't a built-in event is treated as a **custom event**, and its handlers
receive whatever you pass as ``data``. A plain dict is the natural choice:

.. code-block:: python

   # A handler bound by name...
   widget.on("row_imported", lambda e: print(e["row"], e["source"]))

   # ...fires when you emit that event with a payload.
   widget.emit("row_imported", data={"row": 42, "source": "clipboard"})

For a built-in event, pass its matching payload from :mod:`bootstack.events`
instead — the same object an ``on_<event>()`` handler would receive:

.. code-block:: python

   widget.emit("change", data=bs.events.ChangeEvent(value=new_value))

See also
--------

- :doc:`/reference/streams` — chain operators (``debounce``, ``filter``, …)
  onto an event before handling it.
- :doc:`/reference/signals` — bind state to a widget without writing change
  handlers at all.

API reference
-------------

The complete catalog — the curated :class:`Event <bootstack.events.Event>`, the
:class:`Subscription <bootstack.events.Subscription>` handle, and every typed
payload — lives in :doc:`/api-reference/events`. The most common payloads at a
glance:

.. currentmodule:: bootstack.events

.. autosummary::
   :nosignatures:

   Event
   Subscription
   ChangeEvent
   InputEvent
   ValidationEvent
   SelectionEvent
   RowsEvent
   DataChangeEvent
