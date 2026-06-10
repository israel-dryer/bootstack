Tree
====

Tree displays nested data as expandable rows. Reach for it when the *hierarchy
itself* is the point — file trees, document outlines, settings navigation,
grouped pickers. For flat records with columns, sorting, filtering, and paging,
use :doc:`datatable` instead.

Every node is an object *handle*: ``add()`` returns a ``TreeNode`` that you hold
and pass back to ``expand()``, ``select()``, ``remove()``, and the rest — there
are no string ids to track. A node shows an icon and a label, knows its place in
the hierarchy, and carries an open-ended ``data`` bag for your own attributes.

.. image:: /_static/examples/tree-hero-light.png
   :class: bs-screenshot-light
   :alt: Tree — light theme

.. image:: /_static/examples/tree-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Tree — dark theme

Usage
-----

Building the tree
~~~~~~~~~~~~~~~~~

The quickest way to populate a tree is the ``nodes`` argument — a nested list of
specs, where each spec is a label string or a ``dict``. The recognized display
keys are ``label``, ``icon`` (plus ``open_icon`` / ``closed_icon``),
``expanded``, and ``children``; any other key is kept on the node's
:ref:`data bag <tree-data>`.

.. code-block:: python

   bs.Tree(nodes=[
       {
           "label": "src",
           "icon": "folder-fill",
           "expanded": True,
           "children": [
               {"label": "app.py", "icon": "file-earmark-code"},
               {"label": "tree.py", "icon": "file-earmark-code"},
           ],
       },
       {"label": "README.md", "icon": "file-earmark-text"},
   ])

A row shows an optional icon followed by its label — the same content a
``ttk.Treeview`` row gives you, rendered as real widgets. (Richer per-row content
via a custom node renderer is planned for a future release.)

To build the tree imperatively, call ``add()``. It returns a ``TreeNode`` handle
you keep; pass ``parent=`` to nest, or call ``node.add()`` to add a child to a
node you already hold:

.. code-block:: python

   tree = bs.Tree()
   src = tree.add("src", icon="folder-fill", expanded=True)
   tree.add("app.py", parent=src, icon="file-earmark-code")
   button = src.add("button.py", icon="file-earmark-code")   # via the handle

Rearrange the tree at runtime with ``insert()``, ``move()``, ``remove()``, and
``clear()``:

.. code-block:: python

   tree.insert(0, "first.py", parent=src)   # at a specific sibling position
   tree.move(button, parent=None)           # promote to a root node
   tree.remove(src)                         # removes the node and its subtree

Each handle knows its place in the hierarchy through ``node.children``,
``node.parent``, ``node.depth``, ``node.ancestors()``, ``node.descendants()``,
``node.is_leaf``, and ``node.expandable``. Declarative construction doesn't hand
back any handles, so recover them from the tree with ``roots``, ``walk()`` (every
node, depth-first), or ``find(predicate)``:

.. code-block:: python

   tree = bs.Tree(nodes=PROJECT)
   readme = tree.find(lambda n: n.label == "README.md")

.. _tree-data:

Carrying extra data
~~~~~~~~~~~~~~~~~~~~

The display keys (``label``, ``icon`` …) are a *view* over the node, not the node
itself. Whatever you don't spend on a display key rides along on the node's
``data`` dict — passed as ``data=``, as extra keyword arguments to ``add()``, or
as extra keys in a ``nodes=`` spec. Nothing is stripped, so a handler always gets
your own domain object back:

.. code-block:: python

   node = tree.add("invoice.pdf", icon="file-earmark", record_id=42, status="paid")
   node.data["record_id"]   # 42

   tree.on_activate(lambda n: open_record(n.data["record_id"]))

A tree is always in-memory, so ``data`` can hold any Python object — the same
principle :doc:`datatable` and :doc:`listview` records follow
(see :ref:`carrying-extra-data`).

Expanding and lazy loading
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A node with children shows a chevron. Drive expansion programmatically, or
``reveal()`` a deep node to open its ancestors and scroll it into view:

.. code-block:: python

   tree.expand(node)
   tree.collapse(node)
   tree.expand_all()
   tree.collapse_all()
   tree.reveal(deep_node)   # opens ancestors + scrolls into view

Give a node ``open_icon`` and ``closed_icon`` to swap its icon with expansion
state — the classic open/closed folder:

.. code-block:: python

   tree.add("src", open_icon="folder2-open", closed_icon="folder-fill")

When a branch is expensive to build, pass a ``loader`` instead of ``children``.
It runs the first time the node is expanded, receives the node, and returns child
specs (the same format as ``nodes=``); the result is cached. Child specs can
carry their own ``loader``, so deep trees load level by level, and
``reload_children()`` drops and re-fetches a branch:

.. code-block:: python

   def load_children(node):
       records = fetch_from_db(node.data["id"])
       return [{"label": r.name, "icon": "file-earmark"} for r in records]

   tree.add("Reports", icon="folder-fill", loader=load_children)
   tree.reload_children(reports_node)   # later, to refresh

Selection
~~~~~~~~~

``selection_mode`` sets how many nodes can be selected at once: ``'single'``
(default), ``'multi'``, or ``'none'`` for a display-only tree. Set
``show_selection_controls=True`` to show a per-node affordance — a checkbox in
multi mode, a radio in single mode — mirroring :doc:`listview` and
:doc:`datatable`.

.. code-block:: python

   bs.Tree(nodes=PROJECT, selection_mode="single")
   bs.Tree(nodes=PROJECT, selection_mode="multi", show_selection_controls=True)

In multi mode the selection **cascades**: checking a parent checks all of its
descendants, and a partially-checked parent shows a mixed (dash) marker.

.. image:: /_static/examples/tree-selection-light.png
   :class: bs-screenshot-light
   :alt: Tree multi-select cascade — light theme

.. image:: /_static/examples/tree-selection-dark.png
   :class: bs-screenshot-dark
   :alt: Tree multi-select cascade — dark theme

Read the selection through the ``selected_nodes`` property, or change it in code:

.. code-block:: python

   tree.select(node)
   tree.deselect(node)
   tree.select_all()        # multi mode only
   tree.clear_selection()

By default a row click selects the row. Pair ``select_on_click=False`` with
``show_selection_controls=True`` when a click should *open* a node (via
``on_activate``) rather than select it, leaving the control as the only way to
select — the file-explorer pattern.

Events
~~~~~~

All ``on_*`` methods return a ``Subscription`` when called with a handler, or a
``Stream`` when called without one; call ``.cancel()`` on the subscription to
unsubscribe. ``on_selection_changed`` delivers a
:class:`~bootstack.events.TreeSelectionEvent` (with ``nodes``); ``on_activate``,
``on_expand``, and ``on_collapse`` pass the affected ``TreeNode``; and
``on_right_click`` carries enough to position your own menu.

.. code-block:: python

   tree.on_selection_changed(lambda e: print([n.label for n in e.nodes]))
   tree.on_activate(lambda node: open_file(node))          # double-click / Enter
   tree.on_expand(lambda node: print("opened", node.label))
   tree.on_collapse(lambda node: print("closed", node.label))
   tree.on_right_click(lambda e: print(e["node"], e["x_root"], e["y_root"]))

Once focused, the tree is fully keyboard driven: arrow keys move the cursor,
``Left`` / ``Right`` collapse and expand, ``Home`` / ``End`` jump to the first
and last node, ``Enter`` activates, ``Space`` toggles selection, and typing
runs a type-ahead search.

Context menu
~~~~~~~~~~~~

``set_context_menu(builder)`` attaches a per-node right-click menu. The builder
runs on each right-click with the clicked node and a fresh ``ContextMenu`` to
populate, so the items can depend on the node:

.. code-block:: python

   def build(node, menu):
       menu.add_item("Rename", on_click=lambda: rename(node))
       if not node.is_leaf:
           menu.add_item("Expand all", on_click=lambda: tree.expand(node))
       menu.add_separator()
       menu.add_item("Delete", icon="trash", on_click=lambda: tree.remove(node))

   tree.set_context_menu(build)

Pass ``None`` to detach. For full control over positioning, skip the helper and
listen to ``on_right_click`` directly.

Appearance
~~~~~~~~~~

``indent`` sets the per-level indent in pixels, ``striped=True`` alternates row
backgrounds, ``density='compact'`` tightens row height, and ``accent`` colors the
selection. The vertical scrollbar shows by default; pass ``show_scrollbar=False``
to hide it (mousewheel scrolling still works).

.. code-block:: python

   bs.Tree(nodes=PROJECT, indent=24, striped=True, density="compact", accent="success")

.. image:: /_static/examples/tree-density-light.png
   :class: bs-screenshot-light
   :alt: Tree striped compact — light theme

.. image:: /_static/examples/tree-density-dark.png
   :class: bs-screenshot-dark
   :alt: Tree striped compact — dark theme

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

- :doc:`datatable` — flat records with columns, sorting, filtering, and paging.
- :doc:`listview` — a flat virtual list with the same selection model.

API
---

The complete reference for :class:`Tree <bootstack.Tree>` and its
:class:`TreeNode <bootstack.TreeNode>` row handles lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Tree
   ~bootstack.TreeNode

Full Example
------------

.. literalinclude:: ../../docs/examples/tree.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
