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

`tree_nav(source=, parent_field=, label_field=)` projects a **flat adjacency-list**
source — each row names its parent — as a hierarchy. Decorate a builder with
``@shell.detail`` to render the selected node, received as a record dict
(its label is ``text``). A tree opens with nothing selected, so a ``placeholder``
shows in the content area until a node is picked.

.. code-block:: python

   shell.tree_nav(source=files, parent_field="parent_id", label_field="name")

   @shell.detail
   def show(node):
       bs.Label(node["text"], font="heading-lg")

Nodes can also be declared inline with ``tree_nav(nodes=[...])`` when the
hierarchy is small and static rather than backed by a data source.

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
