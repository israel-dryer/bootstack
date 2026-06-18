Master–detail (tree)
====================

A hierarchy in the sidebar drives a detail view — the file explorer, the settings
tree, the category browser. Like the :doc:`list master–detail <master-detail-list>`,
but the records nest under parents.

.. image:: /_static/examples/navigation-master-detail-tree-light.png
   :class: bs-screenshot-light bs-window-screenshot
   :alt: File explorer master–detail — light theme

.. image:: /_static/examples/navigation-master-detail-tree-dark.png
   :class: bs-screenshot-dark bs-window-screenshot
   :alt: File explorer master–detail — dark theme

How it works
------------

`tree_nav` builds the sidebar from a hierarchy and **returns the** `Tree`
**driving it**. Decorate a builder with `@shell.detail` to render the selected
node, received as a record dict (its label is `text`). A tree opens with
nothing selected, so a `placeholder` shows in the content area until a node is
picked.

Declare the hierarchy inline with `nodes=` (each a `{"label", "icon",
"children", ...}` spec; extra keys ride along as the node's data):

.. code-block:: python

   tree = shell.tree_nav(nodes=[
       {"label": "src", "icon": "folder", "children": [
           {"label": "app.py", "icon": "filetype-py", "size": "4.2 KB"},
       ]},
   ])

   @shell.detail
   def show(node):
       with bs.Column(horizontal_items="left", gap=12, padding=(16, 10)):
           bs.Label(node["text"], font="heading-lg")

For large or dynamic hierarchies, pass `source=` instead — a flat
adjacency-list :doc:`data source </reference/data-sources>` where each row names
its parent (`tree_nav(source=files, parent_field="parent_id", label_field="name")`);
the tree then loads each branch lazily as it expands.

Because `tree_nav` hands back the `Tree`, you can drive the view — the file
explorer above opens expanded with a file selected:

.. code-block:: python

   tree.expand_all()
   app = tree.find(lambda node: node.label == "app.py")
   if app is not None:
       tree.select(app)

Example
-------

.. literalinclude:: ../../examples/navigation/master_detail_tree.py
   :language: python
   :linenos:

When to use
-----------

Use the tree master–detail when records form a hierarchy. If the records are
flat, the simpler :doc:`list master–detail <master-detail-list>` reads better.
Note that a tree can't collapse into the icon rail (a branch isn't one glyph), so
under a :doc:`workspace rail <workspaces>` a tree sidebar hides rather than
compacts.
