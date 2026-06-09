Layout & Spacing
================

bootstack arranges widgets with **container** widgets:
:class:`~bootstack.VStack` and :class:`~bootstack.HStack` stack their children
along one axis, and :class:`~bootstack.Grid` places them in rows and columns.
A widget is parented to the nearest enclosing container — the ``with`` block it
is created in.

.. code-block:: python

   with bs.VStack(gap=8, padding=16):
       bs.Label("Name")
       bs.TextField(fill="x")
       with bs.HStack(gap=8):
           bs.Button("OK", fill="x", expand=True)
           bs.Button("Cancel")

Placement options
-----------------

Every widget also accepts **self-placement options** as keyword arguments —
how it sits *within* its parent. Which options apply depends on the parent: a
stack container honors the stack options, a :class:`~bootstack.Grid` honors the
grid options.

.. include:: ../shared/widget-sizing.rst

See also
--------

- :doc:`/widgets/vstack` · :doc:`/widgets/hstack` · :doc:`/widgets/grid` —
  the container widgets.
- :doc:`/widgets/card` · :doc:`/widgets/groupbox` — bordered containers.
