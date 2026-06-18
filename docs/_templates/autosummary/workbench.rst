{{ fullname | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :special-members: __call__
   :exclude-members: tk, var, attach, detach, is_attached, on_attach, on_detach
   :inherited-members:
   :show-inheritance:

Supporting classes
------------------

Opaque handles returned by ``Workbench``'s methods — you obtain them from the
shell rather than constructing them directly. A workspace is a sidebar host, so it
returns the same :class:`~bootstack.widgets.appshell.PageNav` /
:class:`~bootstack.widgets.appshell.Page` handles documented on
:class:`~bootstack.AppShell`.

.. autoclass:: bootstack.widgets.appshell.Workspace
   :members:

.. autoclass:: bootstack.widgets.appshell.Rail
   :members: