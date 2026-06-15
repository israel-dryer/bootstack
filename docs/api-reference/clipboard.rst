Clipboard
=========

.. currentmodule:: bootstack.clipboard

Read and write the system clipboard. The clipboard is global to the running
application, so these are module-level functions rather than per-widget methods;
they operate on the current `App`'s clipboard.

For a task-oriented introduction, see the :doc:`/tasks/clipboard` how-to.

.. autofunction:: get_clipboard

.. autofunction:: set_clipboard