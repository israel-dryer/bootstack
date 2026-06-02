All widgets accept self-placement kwargs via ``**kwargs``. The parent
container determines which options apply — stack-based parents use stack
kwargs, grid-based parents use grid kwargs. Unrecognised keys are
silently ignored.

Stack
'''''

Used inside ``VStack``, ``HStack``, ``App``, and other stack containers.

.. list-table::
   :widths: 25 75

   * - ``fill``
     - Fill direction: ``'x'``, ``'y'``, ``'both'``, or ``'none'``.
   * - ``expand``
     - Grow to consume extra space in the parent. ``True`` or ``False``.
   * - ``anchor``
     - Alignment when the widget does not fill the available slot:
       ``'n'``, ``'s'``, ``'e'``, ``'w'``, ``'center'``, ``'nw'``,
       etc.
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
   * - ``sticky``
     - Alignment and fill within the grid cell. Any combination of
       ``'n'``, ``'s'``, ``'e'``, ``'w'`` — e.g. ``'ew'`` stretches
       horizontally, ``'nsew'`` fills the entire cell.
   * - ``margin``
     - External spacing in pixels. Accepts an integer, a 2-tuple
       ``(horizontal, vertical)``, or a 4-tuple ``(left, top, right, bottom)``.
   * - ``margin_x``
     - Horizontal external spacing. Accepts an integer or ``(left, right)``.
   * - ``margin_y``
     - Vertical external spacing. Accepts an integer or ``(top, bottom)``.
