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
   ThemeToggle

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

Visualization
-------------

Data visualization. ``Chart`` embeds a matplotlib figure as a themed widget —
recoloring with light/dark, live-updating from a `Signal` or a data source, and
optionally seeding seaborn's palette from the theme accents. Requires the
optional ``viz`` (or ``viz-seaborn``) extra.

.. autosummary::
   :nosignatures:

   Chart

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
   Column
   Divider
   Grid
   GroupBox
   Row
   ScrollView
   Spacer
   SplitPane
   SplitView

Navigation
----------

Multi-page containers — swap pages with ``PageStack`` or tab between them with
``Tabs``. Each parent hands back typed page handles (``StackPage``, ``TabPage``).
For a full application sidebar, use :class:`~bootstack.AppShell`.

.. autosummary::
   :nosignatures:

   PageStack
   StackPage
   TabPage
   Tabs

Chrome bars and menus
---------------------

Window chrome strips — a toolbar, a passive status bar, a window menu bar, a
dropdown menu button, and a right-click context menu.

.. autosummary::
   :nosignatures:

   ContextMenu
   ContextMenuItem
   StatusBar
   Toolbar
   MenuButton

Overlays
--------

Transient, floating UI — hover tooltips and the three message surfaces
(passive toast, persistent notification, and in-app snackbar).

.. autosummary::
   :nosignatures:

   Notification
   Snackbar
   Tooltip
   snackbar
   toast

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
      Chart
      Checkbox
      CodeEditor
      Column
      ContextMenu
      ContextMenuItem
      DataTable
      DateField
      Divider
      FieldItem
      Form
      FormItem
      Gallery
      Gauge
      Grid
      GroupBox
      GroupItem
      Label
      ListView
      MenuButton
      Notification
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
      Row
      ScrollView
      Select
      SelectButton
      Slider
      Snackbar
      snackbar
      Spacer
      SpinnerField
      SplitPane
      SplitView
      StackPage
      StatusBar
      Switch
      TabItem
      TabPage
      Tabs
      TabsItem
      TextArea
      TextField
      ThemeToggle
      TimeField
      toast
      ToggleButton
      ToggleGroup
      Toolbar
      Tooltip
      Tree
      TreeNode
