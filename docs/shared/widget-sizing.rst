All widgets accept placement kwargs via ``**kwargs``. The framework
automatically detects which geometry manager to use based on the keys
provided.

Pack (default)
''''''''''''''

Used when no grid or place trigger keys are present. Most widgets in a
``VStack``, ``HStack``, or ``App`` context use pack.

.. list-table::
   :widths: 25 75

   * - ``fill``
     - Fill direction: ``'x'``, ``'y'``, ``'both'``, or ``'none'``.
   * - ``expand``
     - Grow to consume extra space in the parent. ``True`` or ``False``.
   * - ``side``
     - Edge to pack against: ``'top'`` (default), ``'bottom'``,
       ``'left'``, ``'right'``.
   * - ``anchor``
     - Alignment when the widget does not fill the pack slot:
       ``'n'``, ``'s'``, ``'e'``, ``'w'``, ``'center'``, ``'nw'``,
       etc.
   * - ``padx`` / ``pady``
     - External horizontal / vertical padding in pixels.
   * - ``ipadx`` / ``ipady``
     - Internal horizontal / vertical padding in pixels.
   * - ``margin``
     - Bootstack shorthand — sets equal ``padx`` and ``pady``.
   * - ``before`` / ``after``
     - Pack immediately before or after a specific sibling widget.

Grid
''''

Used when ``row=`` or ``column=`` is present. Widgets placed inside a
``Grid`` container use grid.

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
   * - ``padx`` / ``pady``
     - External horizontal / vertical padding in pixels.
   * - ``ipadx`` / ``ipady``
     - Internal horizontal / vertical padding in pixels.
   * - ``margin``
     - Bootstack shorthand — sets equal ``padx`` and ``pady``.

Place
'''''

Used when ``x=``, ``y=``, ``relx=``, or ``rely=`` is present. Useful
for fixed or proportional absolute positioning.

.. list-table::
   :widths: 25 75

   * - ``x`` / ``y``
     - Absolute position in pixels from the top-left of the parent.
   * - ``relx`` / ``rely``
     - Relative position as a fraction of the parent size (0.0–1.0).
   * - ``width`` / ``height``
     - Absolute widget size in pixels.
   * - ``relwidth`` / ``relheight``
     - Relative size as a fraction of the parent size (0.0–1.0).
   * - ``anchor``
     - Which point of the widget is placed at the given position:
       ``'nw'`` (default), ``'center'``, etc.
   * - ``bordermode``
     - Coordinate reference: ``'inside'`` (default) or ``'outside'``.
