All widgets accept self-placement kwargs via ``**kwargs``. The parent
container determines which options apply — ``Column`` / ``Row`` parents use
the stacking kwargs below, grid-based parents use grid kwargs.

Column (vertical stacks)
''''''''''''''''''''''''

Used inside a ``Column``, ``App``, or any other vertical stack. Children stack
top-to-bottom, so ``horizontal`` aligns each child across the band and ``grow``
shares the vertical space. (``vertical`` does not apply — the stacking order sets
the top-to-bottom position.)

.. list-table::
   :widths: 25 75

   * - ``horizontal``
     - Cross-axis placement of the widget: ``'left'``, ``'center'``,
       ``'right'``, or ``'stretch'`` to fill the available width.
   * - ``grow``
     - Claim and fill a share of the leftover **vertical** space (the stacking
       axis). ``True`` or ``False``.
   * - ``margin``
     - External spacing in pixels. Accepts an integer (equal on all
       sides), a 2-tuple ``(horizontal, vertical)``, or a 4-tuple
       ``(left, top, right, bottom)``.
   * - ``margin_x``
     - Horizontal external spacing (left and right). Accepts an integer
       or a 2-tuple ``(left, right)`` for asymmetric spacing. Overrides
       the horizontal component of ``margin=``.
   * - ``margin_y``
     - Vertical external spacing (top and bottom). Accepts an integer
       or a 2-tuple ``(top, bottom)`` for asymmetric spacing. Overrides
       the vertical component of ``margin=``.

Row (horizontal stacks)
'''''''''''''''''''''''

Used inside a ``Row`` or any other horizontal stack. Children stack
left-to-right, so ``vertical`` aligns each child across the band and ``grow``
shares the horizontal space. (``horizontal`` does not apply — the stacking order
sets the left-to-right position.)

.. list-table::
   :widths: 25 75

   * - ``vertical``
     - Cross-axis placement of the widget: ``'top'``, ``'center'``,
       ``'bottom'``, or ``'stretch'`` to fill the available height.
   * - ``grow``
     - Claim and fill a share of the leftover **horizontal** space (the stacking
       axis). ``True`` or ``False``.
   * - ``margin``
     - External spacing in pixels. Accepts an integer (equal on all
       sides), a 2-tuple ``(horizontal, vertical)``, or a 4-tuple
       ``(left, top, right, bottom)``.
   * - ``margin_x``
     - Horizontal external spacing (left and right). Accepts an integer
       or a 2-tuple ``(left, right)`` for asymmetric spacing. Overrides
       the horizontal component of ``margin=``.
   * - ``margin_y``
     - Vertical external spacing (top and bottom). Accepts an integer
       or a 2-tuple ``(top, bottom)`` for asymmetric spacing. Overrides
       the vertical component of ``margin=``.

Grid
''''

Used inside a ``Grid`` container.

.. list-table::
   :widths: 25 75

   * - ``row`` / ``column``
     - Zero-based row and column indices.
   * - ``rowspan`` / ``columnspan``
     - Number of rows or columns to span.
   * - ``horizontal``
     - Horizontal placement within the grid cell: ``'left'``,
       ``'center'``, ``'right'``, or ``'stretch'`` to fill the cell width.
   * - ``vertical``
     - Vertical placement within the grid cell: ``'top'``, ``'center'``,
       ``'bottom'``, or ``'stretch'`` to fill the cell height.
   * - ``margin``
     - External spacing in pixels. Accepts an integer, a 2-tuple
       ``(horizontal, vertical)``, or a 4-tuple ``(left, top, right, bottom)``.
   * - ``margin_x``
     - Horizontal external spacing. Accepts an integer or ``(left, right)``.
   * - ``margin_y``
     - Vertical external spacing. Accepts an integer or ``(top, bottom)``.
