Types
=====

.. currentmodule:: bootstack.types

Token and keyword types for annotating your own helpers and widget subclasses.
These are the names that appear in widget signatures — the accent/variant/surface
tokens, the layout literals, density, and the keyword ``TypedDict``\ s. Import them
from ``bootstack.types`` when you annotate code that builds on bootstack::

    from bootstack.types import AccentToken, WidgetDensity

Style tokens
------------

Semantic tokens for color, variant, surface, density, and window effects.

.. autosummary::
   :toctree: generated
   :nosignatures:

   AccentToken
   SurfaceToken
   VariantToken
   WidgetDensity
   WindowStyle

Layout literals
---------------

The placement and sizing literals accepted by container and ``**kwargs`` layout
options.

.. autosummary::
   :toctree: generated
   :nosignatures:

   Anchor
   AutoFlow
   Fill
   LayoutKind
   Padding
   Side
   Sticky

Keyword and config types
------------------------

The ``TypedDict`` shapes for low-level widget options and the data-entry config
that ``DataTable`` and ``Form`` accept.

.. autosummary::
   :toctree: generated
   :nosignatures:

   BaseWidgetKwargs
   ColumnSpec
   EditorType
   FormOptions
   StyledKwargs
