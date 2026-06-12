Events
======

.. currentmodule:: bootstack.events

The event catalog. Every widget announces what it does as a named event;
data-carrying events hand the handler a typed payload, while native events hand
it a curated, toolkit-free :class:`Event`. This module is the home of all of
those types, so editors can autocomplete the attributes on each one.

For a task-oriented introduction — listening, reading a payload, cancelling a
subscription, emitting your own — see the :doc:`/reference/events` guide.

Event handling
--------------

The curated event handed to native handlers and the cancellable handle returned
by every binding.

.. autosummary::
   :toctree: generated
   :nosignatures:

   Event
   Subscription

Value and input payloads
------------------------

Handed to handlers for value commits, live input, validation, and toggles.

.. autosummary::
   :toctree: generated
   :nosignatures:

   ChangeEvent
   InputEvent
   ValidationEvent
   TextModifiedEvent
   ToggleEvent

Slider payloads
---------------

The live and committed payloads for the single- and range-value sliders.

.. autosummary::
   :toctree: generated
   :nosignatures:

   SliderEvent
   SliderCommitEvent
   RangeSliderEvent
   RangeSliderCommitEvent

Date payloads
-------------

.. autosummary::
   :toctree: generated
   :nosignatures:

   DateSelectEvent

Navigation and layout payloads
------------------------------

Page, nav-pane, display-mode, and accordion activity.

.. autosummary::
   :toctree: generated
   :nosignatures:

   PageChangeEvent
   NavEvent
   PaneToggleEvent
   DisplayModeEvent
   AccordionChangeEvent

Tab payloads
------------

The change/activate/deactivate/close payloads for a tab strip.

.. autosummary::
   :toctree: generated
   :nosignatures:

   TabChangeEvent
   TabActivateEvent
   TabDeactivateEvent
   TabCloseEvent

Data and selection payloads
---------------------------

Row CRUD, selection, export, tree selection, button-group clicks, menu
selection, and the data-source change broadcast.

.. autosummary::
   :toctree: generated
   :nosignatures:

   RowEvent
   RowsEvent
   SelectionEvent
   TreeSelectionEvent
   ExportEvent
   ButtonGroupClickEvent
   MenuSelectEvent
   DataChangeEvent

Picture and media payloads
--------------------------

The load and error events fired by :class:`Picture <bootstack.Picture>` as it
decodes and displays an image.

.. autosummary::
   :toctree: generated
   :nosignatures:

   ImageLoadEvent
   ImageErrorEvent

Supporting types
----------------

Value types carried *inside* payloads, rather than handed to a handler directly.

.. autosummary::
   :toctree: generated
   :nosignatures:

   TabRef

Enumerations
------------

The string-literal tags carried by the change and data-change payloads.

.. py:type:: ChangeKind

   What a data-source change describes — `'load'`, `'insert'`, `'update'`,
   `'delete'`, `'move'`, `'filter'`, `'sort'`, `'reload'`, `'select'`.

.. py:type:: ChangeMethod

   How a change was made — `'click'`, `'key'`, `'programmatic'`, `'unknown'`.

.. py:type:: ChangeReason

   Why a change event fired — `'user'`, `'api'`, `'hide'`, `'forget'`,
   `'unknown'`.
