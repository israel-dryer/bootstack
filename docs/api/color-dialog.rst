Color Dialog
============

``bs.ask_color()`` opens a modal color chooser and returns the selected color.
``bs.ColorChooserDialog`` gives the same chooser as a reusable object.

.. code-block:: python

   result = bs.ask_color(color="#0070C0")
   if result:
       print(result.hex)        # '#0070c0'
       print(result.rgb)        # (0, 112, 192)
       print(result.hsl)        # (205, 100, 37)

.. raw:: html

   <img class="bs-screenshot-light bs-dialog-screenshot"
        src="/_static/examples/color-dialog-light.png"
        alt="Color Dialog demo — light theme"
        style="max-width:100%; margin:1rem 0;">
   <img class="bs-screenshot-dark bs-dialog-screenshot"
        src="/_static/examples/color-dialog-dark.png"
        alt="Color Dialog demo — dark theme"
        style="max-width:100%; margin:1rem 0;">

Usage
-----

Convenience function
~~~~~~~~~~~~~~~~~~~~

``bs.ask_color()`` is the one-liner shorthand. Pass ``color=`` to pre-select an
initial color (any CSS hex string):

.. code-block:: python

   result = bs.ask_color(title="Background Color", color="#1a1a2e")
   if result:
       apply_background(result.hex)

The return value is a ``ColorChoice`` with three attributes:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Attribute
     - Description
   * - ``rgb``
     - ``(r, g, b)`` tuple, each 0–255.
   * - ``hsl``
     - ``(h, s, l)`` tuple: hue 0–360, saturation and luminance 0–100.
   * - ``hex``
     - Lowercase hex string, e.g. ``'#0070c0'``.

``None`` is returned if the user cancels.

Reusable dialog object
~~~~~~~~~~~~~~~~~~~~~~

Use ``bs.ColorChooserDialog`` when you need to inspect the result after ``show()``
or show the same dialog multiple times:

.. code-block:: python

   dlg = bs.ColorChooserDialog(title="Pick a color", color="#ff0000")
   dlg.show()

   if dlg.result:
       r, g, b = dlg.result.rgb

Chooser layout
~~~~~~~~~~~~~~

The dialog shows a hue/saturation spectrum with a luminance slider below it.
Numeric fields on the right allow direct entry in RGB, HSL, or hex notation.
A dropper button (Windows/Linux only) lets the user sample any pixel on the
desktop.

See also
--------

:doc:`input-dialogs` — ``ask_string()``, ``ask_integer()``, and other value-input dialogs.

:doc:`font-dialog` — ``ask_font()`` for selecting a font.

API
---

.. autofunction:: bootstack.widgets.dialogs.ask_color

.. autoclass:: bootstack.widgets.dialogs.ColorChooserDialog
   :members:

Full Example
------------

.. literalinclude:: ../../docs/examples/color-dialog.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs