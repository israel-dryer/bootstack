bootstack
=========

.. currentmodule:: bootstack

The top-level namespace — everything you compose a UI from. Widgets, the
application shells, reactive state, and the dialog and theme verbs are all
importable directly as ``bootstack.<name>`` (commonly ``import bootstack as bs``).

Everything you reference *by type to configure behavior* — data sources, events,
validation rules, tokens — lives in a submodule; see the other pages in this
section.

.. note::

   This page is being built out. The reactive-state and theme entries below are
   in place; the widget catalog and dialog verbs follow. Until then, the
   :doc:`/widgets/index` catalog documents each widget with usage and examples.

Application
-----------

The application object and top-level windows. ``App`` is the root of a simple
app; ``AppShell`` adds a toolbar, navigation pane, and paged content.

.. autosummary::
   :toctree: generated
   :nosignatures:

   App
   AppShell
   Window

State
-----

The reactive value that binds application state to widgets.

.. autosummary::
   :toctree: generated
   :nosignatures:
   :template: signal

   Signal

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

Data Display
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

Theme
-----

Switch the active theme at runtime. (Declaring themes and the other theme/font
functions live in :doc:`/api-reference/style`.)

.. autosummary::
   :toctree: generated
   :nosignatures:

   set_theme
   toggle_theme
