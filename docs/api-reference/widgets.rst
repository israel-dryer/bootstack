Widgets
=======

.. currentmodule:: bootstack

Every visual component you place inside a window — actions, inputs, selection
controls, data displays, layout containers, and navigation. All are importable
directly as ``bootstack.<name>`` (commonly ``import bootstack as bs``). For
usage, screenshots, and worked examples, see the :doc:`/widgets/index` catalog;
this page is the complete lookup reference.

Actions
-------

Buttons and button groups for triggering commands.

.. autosummary::
   :nosignatures:

   Button
   ButtonGroup

Inputs
------

Text, number, path, date/time, and slider inputs. Most bind to a ``signal=`` /
``textsignal=`` and support validation ``rules=``.

.. autosummary::
   :nosignatures:

   CodeEditor
   DateField
   NumberField
   PasswordField
   PathField
   RangeSlider
   Slider
   SpinnerField
   TextArea
   TextField
   TimeField

Selection
---------

Checkboxes, switches, radio and toggle groups, dropdowns, and the calendar.
``RadioGroup`` is built from ``Radio`` / ``RadioToggleButton`` items.

.. autosummary::
   :nosignatures:

   Calendar
   Checkbox
   Radio
   RadioGroup
   RadioToggleButton
   Select
   SelectButton
   Switch
   ToggleButton
   ToggleGroup

Data display
------------

Read-only views of values and records — text and badges, progress and gauges,
and the list, table, and tree views for collections. ``ListView``, ``DataTable``,
and ``Tree`` bind to a ``data_source=``; ``Tree`` exposes its rows as ``TreeNode``
handles.

.. autosummary::
   :nosignatures:

   Badge
   DataTable
   Gauge
   Label
   ListView
   ProgressBar
   Tree
   TreeNode

Media
-----

Image and media display. ``Picture`` shows an :class:`Image <bootstack.images.Image>`
scaled to fit, with fit modes, rounded corners, and animated-GIF playback; ``Gallery``
is a record-native, recycling grid of selectable thumbnails; ``Carousel`` steps through
image slides one at a time with transitions and autoplay; ``Avatar`` is a small identity
badge showing a picture or initials.

.. autosummary::
   :nosignatures:

   Avatar
   Carousel
   Gallery
   Picture

Layout
------

Containers that arrange children — stacks, grids, and scroll regions, plus the
framed and collapsible groupings. ``Accordion`` exposes its sections as
``AccordionSection`` handles and ``SplitView`` its panes as ``SplitPane`` handles.

.. autosummary::
   :nosignatures:

   Accordion
   AccordionSection
   Card
   Grid
   GroupBox
   HStack
   ScrollView
   Separator
   SplitPane
   SplitView
   VStack

Navigation
----------

Multi-page containers — swap pages with ``PageStack``, tab between them with
``Tabs``, or drive a sidebar with ``SideNav``. Each parent hands back typed page
and item handles (``StackPage``, ``TabPage``, and the ``SideNav*`` items).

.. autosummary::
   :nosignatures:

   PageStack
   SideNav
   SideNavGroup
   SideNavHeader
   SideNavItem
   SideNavSeparator
   StackPage
   TabPage
   Tabs

Menus and command bars
----------------------

Command surfaces — a window menu bar, a command bar strip, a dropdown menu button,
and a right-click context menu.

.. autosummary::
   :nosignatures:

   CommandBar
   ContextMenu
   ContextMenuItem
   MenuButton

Overlays
--------

Transient, floating UI — hover tooltips and dismissible toast notifications.

.. autosummary::
   :nosignatures:

   Toast
   Tooltip

Forms
-----

A declarative form builder and the item types that describe its layout — fields,
groups, and tabbed sections.

.. autosummary::
   :nosignatures:

   FieldItem
   Form
   FormItem
   GroupItem
   TabItem
   TabsItem

..
   Hidden, globally-alphabetical toctree. The grouped tables above are
   display-only (no :toctree:); this single block generates every stub and
   drives the sidebar nav as one sorted A–Z list, rather than the group order
   the grouped blocks would otherwise produce.

.. container:: bs-hidden-summary

   .. autosummary::
      :toctree: generated
      :nosignatures:

      Accordion
      AccordionSection
      Avatar
      Badge
      Button
      ButtonGroup
      Calendar
      Card
      Carousel
      Checkbox
      CodeEditor
      CommandBar
      ContextMenu
      ContextMenuItem
      DataTable
      DateField
      FieldItem
      Form
      FormItem
      Gallery
      Gauge
      Grid
      GroupBox
      GroupItem
      HStack
      Label
      ListView
      MenuButton
      NumberField
      PageStack
      PasswordField
      PathField
      Picture
      ProgressBar
      Radio
      RadioGroup
      RadioToggleButton
      RangeSlider
      ScrollView
      Select
      SelectButton
      Separator
      SideNav
      SideNavGroup
      SideNavHeader
      SideNavItem
      SideNavSeparator
      Slider
      SpinnerField
      SplitPane
      SplitView
      StackPage
      Switch
      TabItem
      TabPage
      Tabs
      TabsItem
      TextArea
      TextField
      TimeField
      Toast
      ToggleButton
      ToggleGroup
      Tooltip
      Tree
      TreeNode
      VStack
