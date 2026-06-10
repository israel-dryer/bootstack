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
   :toctree: generated
   :nosignatures:

   Button
   ButtonGroup

Inputs
------

Text, number, path, date/time, and slider inputs. Most bind to a ``signal=`` /
``textsignal=`` and support validation ``rules=``.

.. autosummary::
   :toctree: generated
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
   :toctree: generated
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
   :toctree: generated
   :nosignatures:

   Badge
   DataTable
   Gauge
   Label
   ListView
   ProgressBar
   Tree
   TreeNode

Layout
------

Containers that arrange children — stacks, grids, and scroll regions, plus the
framed and collapsible groupings. ``Accordion`` exposes its sections as
``AccordionSection`` handles and ``SplitView`` its panes as ``SplitPane`` handles.

.. autosummary::
   :toctree: generated
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
   :toctree: generated
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
