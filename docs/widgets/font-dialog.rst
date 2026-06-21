Font Dialog
===========

``bs.ask_font()`` opens a modal font selector and returns the selected font.
``FontDialog`` gives the same selector as a reusable object.

.. image:: /_static/examples/font-dialog-hero-light.png
   :class: bs-screenshot-light bs-dialog-screenshot
   :alt: Font Dialog — light theme

.. image:: /_static/examples/font-dialog-hero-dark.png
   :class: bs-screenshot-dark bs-dialog-screenshot
   :alt: Font Dialog — dark theme

Usage
-----

Reach for the ``ask_font()`` verb by default — it covers the one-shot case. Drop
to the ``FontDialog`` object only when you need to reuse the selector or open it
repeatedly.

Convenience function
~~~~~~~~~~~~~~~~~~~~

``bs.ask_font()`` is the one-liner shorthand. Pass ``default_font=`` a font
token to pre-select the starting font:

.. code-block:: python

   choice = bs.ask_font(title="Body Font")
   if choice:
       print(choice.family)   # e.g. 'Segoe UI'
       print(choice.size)     # e.g. 11

The return value is a ``FontChoice`` with six attributes:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Attribute
     - Description
   * - ``family``
     - Font family name, e.g. ``'Segoe UI'``.
   * - ``size``
     - Point size (int).
   * - ``weight``
     - ``'normal'`` or ``'bold'``.
   * - ``slant``
     - ``'roman'`` or ``'italic'``.
   * - ``underline``
     - ``True`` if underlined.
   * - ``overstrike``
     - ``True`` if struck through.

``default_font=`` accepts any font token (``'body'``, ``'code'``,
``'heading-lg'``, …); it defaults to ``'body'``. See :doc:`/reference/typography`
for the full token list. ``None`` is returned if the user cancels.

Reusable dialog object
~~~~~~~~~~~~~~~~~~~~~~

Use ``FontDialog`` when you need to inspect the result after ``show()``:

.. code-block:: python

   from bootstack.dialogs import FontDialog

   dlg = FontDialog(title="Code Font", default_font="code")
   dlg.show()

   if dlg.result:
       family = dlg.result.family
       size   = dlg.result.size

Using the result
~~~~~~~~~~~~~~~~

``FontChoice`` is a plain namedtuple, so its fields read directly:

.. code-block:: python

   choice = bs.ask_font()
   if choice:
       print(f"{choice.family} {choice.size}pt "
             f"{choice.weight} {choice.slant}")

See also
--------

:doc:`color-dialog` — ``ask_color()`` for choosing a color.

:doc:`input-dialogs` — ``ask_string()``, ``ask_integer()``, and other value-input dialogs.

API
---

The complete reference for :func:`ask_font() <bootstack.ask_font>` and
:class:`FontDialog <bootstack.dialogs.FontDialog>` (and its ``FontChoice`` result)
lives on the :doc:`Dialogs </api-reference/dialogs>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.ask_font
   ~bootstack.dialogs.FontDialog
   ~bootstack.dialogs.FontChoice

Full Example
------------

.. literalinclude:: ../../docs/examples/font-dialog.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs