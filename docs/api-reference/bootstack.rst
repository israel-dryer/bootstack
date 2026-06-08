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

State
-----

The reactive value that binds application state to widgets.

.. autosummary::
   :toctree: generated
   :nosignatures:
   :template: signal

   Signal

Theme
-----

Switch the active theme at runtime. (Declaring themes and the other theme/font
functions live in :doc:`/api-reference/style`.)

.. autosummary::
   :toctree: generated
   :nosignatures:

   set_theme
   toggle_theme
