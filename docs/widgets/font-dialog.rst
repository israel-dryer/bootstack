Font Dialog
===========

``bs.ask_font()`` opens a modal font selector and returns the selected font.
``bs.FontDialog`` gives the same selector as a reusable object.

.. image:: /_static/examples/font-dialog-hero-light.png
   :class: bs-screenshot-light bs-dialog-screenshot
   :alt: Font Dialog — light theme

.. image:: /_static/examples/font-dialog-hero-dark.png
   :class: bs-screenshot-dark bs-dialog-screenshot
   :alt: Font Dialog — dark theme

Usage
-----

Convenience function
~~~~~~~~~~~~~~~~~~~~

``bs.ask_font()`` is the one-liner shorthand. Pass ``default_font=`` to
pre-select a starting font by name:

.. code-block:: python

   font = bs.ask_font(title="Body Font")
   if font:
       print(font.actual()["family"])   # e.g. 'Segoe UI'
       print(font.actual()["size"])     # e.g. 11

Built-in font names accepted by ``default_font=``:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Name
     - Description
   * - ``'TkDefaultFont'``
     - System UI font (default).
   * - ``'TkTextFont'``
     - Font used in text editors.
   * - ``'TkFixedFont'``
     - Monospace font.
   * - ``'TkHeadingFont'``
     - Font used in list/tree column headings.

``None`` is returned if the user cancels.

Reusable dialog object
~~~~~~~~~~~~~~~~~~~~~~

Use ``bs.FontDialog`` when you need to inspect the result after ``show()``:

.. code-block:: python

   dlg = bs.FontDialog(title="Code Font", default_font="TkFixedFont")
   dlg.show()

   if dlg.result:
       family = dlg.result.actual()["family"]
       size   = dlg.result.actual()["size"]

Using the returned font
~~~~~~~~~~~~~~~~~~~~~~~

The returned object supports standard font introspection and can be passed
directly to widgets that accept a font:

.. code-block:: python

   font = bs.ask_font()
   if font:
       info = font.actual()
       print(f"{info['family']} {info['size']}pt "
             f"{info['weight']} {info['slant']}")

See also
--------

:doc:`color-dialog` — ``ask_color()`` for choosing a color.

:doc:`input-dialogs` — ``ask_string()``, ``ask_integer()``, and other value-input dialogs.

API
---

.. autofunction:: bootstack.widgets.dialogs.ask_font

.. autoclass:: bootstack.widgets.dialogs.FontDialog
   :members:

Full Example
------------

.. literalinclude:: ../../docs/examples/font-dialog.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs