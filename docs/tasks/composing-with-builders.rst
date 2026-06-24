Composing with Builders
=======================

A builder function is any plain function that *builds widgets*. Because a widget
finds its parent from the **active container** at the moment it is constructed —
not from where it was defined — a function that creates widgets is automatically
a reusable, location-agnostic component. No base class, no registration, no
threading a ``parent=`` argument through your code: the function simply paints
into whatever container is open when you call it.

This is the same idea already behind pages (``with shell.add_page("home"): ...``)
and dialog bodies (``Dialog(content_builder=...)``) and hot reload
(:doc:`/production/hot-reload` re-invokes a builder into its region). Naming it
once makes all of them read as a single pattern.

The mental model
----------------

Every widget you create mounts into the container that is currently open on the
context stack — the ``with bs.Column():`` (or ``App``, ``Card``, page, …) you are
inside of. A builder function just defers that creation:

.. code-block:: python

   import bootstack as bs

   def action_bar():
       with bs.Row(gap=8):
           bs.Button("Save", accent="primary")
           bs.Button("Cancel", accent="default")

   with bs.App() as app:
       bs.Label("Settings", font="heading-lg")
       action_bar()          # paints into the App's content area
       with bs.Card():
           action_bar()      # the SAME function paints into the Card

The function is resolved at *call* time, so the one definition serves both
locations. It is not a closure over a particular parent — call it wherever you
need that piece of UI.

Parameterizing a component
--------------------------

Pass data in as arguments. A builder that takes a record is a reusable
component:

.. code-block:: python

   def user_card(user):
       with bs.Card(gap=4):
           bs.Avatar(image=user.avatar)
           bs.Label(user.name, font="heading-md")
           bs.Label(user.email, accent="muted")

   with bs.Column(gap=12):
       for user in people:
           user_card(user)

Returning a handle
------------------

A builder can return whatever the caller needs to wire up later — a
:doc:`/reference/signals` for the value it manages, a widget reference, or a
small bundle:

.. code-block:: python

   def search_box(placeholder="Search..."):
       query = bs.Signal("")
       bs.TextField(textsignal=query, placeholder=placeholder)
       return query

   with bs.App() as app:
       query = search_box()
       query.subscribe(run_search)

Composing builders
------------------

Builders call builders. Each one paints into whatever container is active when
it runs, so they nest naturally:

.. code-block:: python

   def toolbar_row():
       with bs.Row(gap=8, horizontal="stretch", horizontal_items="right"):
           bs.Button("New")
           bs.Button("Refresh")

   def page_body(records):
       toolbar_row()
       with bs.Card():
           for record in records:
               user_card(record)

   with shell.add_page("people", text="People", icon="people"):
       page_body(records)

The one rule
------------

A builder needs an open container (or an explicit ``parent=``) so its widgets
have somewhere to mount. Call one with neither and you get a clear error at the
first widget, rather than a confusing failure later:

.. code-block:: python

   user_card(user)        # at module level, outside any `with` block
   # BootstackError: Avatar was created outside any container and without
   # parent=. Create it inside a layout context (e.g. `with bs.App():` or
   # `with bs.Column():`), or pass parent=<container>.

So the rule is simply: **call a builder inside a layout context.** That is the
only constraint the pattern imposes.

A note on shared state
----------------------

A builder *builds* — it should read state, not own durable state. Keep
long-lived signals, data sources, and stores in the module (or pass them in) and
let builders render them. This keeps components reusable, and it is what makes a
builder safe to re-run — for example when :doc:`/production/hot-reload` rebuilds
a page on save.

See also
--------

- :doc:`/production/hot-reload` — ``@reloadable`` marks a builder so only its
  region rebuilds on save; builders are what make per-page reload possible.
- :doc:`/tasks/navigation/index` — a page body is a builder painting into the
  page's content area.
- :doc:`/tasks/dialogs` — ``content_builder`` is a builder painting into the
  dialog's content area.
- :doc:`/tasks/composing-fields` — building reusable field components.
