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

Opaque handles returned by ``AppShell``'s methods — you obtain them from the shell
rather than constructing them directly. (The status band is a standalone widget;
see :class:`~bootstack.StatusBar`.)

.. autoclass:: bootstack.widgets.appshell.PageNav
   :members:

.. autoclass:: bootstack.widgets.appshell.Page
   :members:
