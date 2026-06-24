Application
===========

.. currentmodule:: bootstack

The application object and top-level windows. ``App`` is the root of a simple
app; ``AppShell`` adds a toolbar stack, one navigation sidebar, and paged content;
``Workbench`` is the two-tier variant with a workspace rail. ``Window`` opens a
secondary top-level window, and ``Splash`` shows a borderless intro screen while
the app starts.

.. autosummary::
   :toctree: generated
   :nosignatures:
   :template: toplevel

   App

.. autosummary::
   :toctree: generated
   :nosignatures:
   :template: appshell

   AppShell

.. autosummary::
   :toctree: generated
   :nosignatures:
   :template: workbench

   Workbench

.. autosummary::
   :toctree: generated
   :nosignatures:
   :template: toplevel

   Window

.. autosummary::
   :toctree: generated
   :nosignatures:
   :template: toplevel

   Splash

The :class:`AppShell <bootstack.AppShell>` reference documents its ``PageNav`` and
``Page`` handles, and :class:`Workbench <bootstack.Workbench>` its ``Workspace``
and ``Rail`` handles, each in a *Supporting classes* section.
