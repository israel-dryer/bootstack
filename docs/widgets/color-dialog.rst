Color Dialog
============

``bs.ask_color()`` opens a modal color chooser and returns the selected color.
``ColorChooserDialog`` gives the same chooser as a reusable object.

.. image:: /_static/examples/color-dialog-hero-light.png
   :class: bs-screenshot-light bs-dialog-screenshot
   :alt: Color Dialog — light theme

.. image:: /_static/examples/color-dialog-hero-dark.png
   :class: bs-screenshot-dark bs-dialog-screenshot
   :alt: Color Dialog — dark theme

Usage
-----

Convenience function
~~~~~~~~~~~~~~~~~~~~

``bs.ask_color()`` is the one-liner shorthand. Pass ``value=`` to pre-select an
initial color (any CSS hex string):

.. code-block:: python

   result = bs.ask_color(title="Background Color", value="#1a1a2e")
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

Use ``ColorChooserDialog`` when you need to inspect the result after ``show()``
or show the same dialog multiple times:

.. code-block:: python

   from bootstack.dialogs import ColorChooserDialog

   dlg = ColorChooserDialog(title="Pick a color", value="#ff0000")
   dlg.show()

   if dlg.result:
       r, g, b = dlg.result.rgb

Chooser layout
~~~~~~~~~~~~~~

The chooser has two tabs. **Themed** shows the active theme's color families
(primary, success, info, warning, danger, and a neutral gray) as light-to-dark
bands — click any swatch to pick an on-theme color. **Custom** shows a
hue/saturation field for picking any color freely. Both tabs share the luminance
slider, live preview, and the numeric fields on the right, which allow direct
entry in RGB, HSL, or hex notation.

.. image:: /_static/examples/color-dialog-custom-light.png
   :class: bs-screenshot-light bs-dialog-screenshot
   :alt: Color Dialog custom tab — light theme

.. image:: /_static/examples/color-dialog-custom-dark.png
   :class: bs-screenshot-dark bs-dialog-screenshot
   :alt: Color Dialog custom tab — dark theme

See also
--------

:doc:`input-dialogs` — ``ask_string()``, ``ask_integer()``, and other value-input dialogs.

:doc:`font-dialog` — ``ask_font()`` for selecting a font.

API
---

The complete reference for :func:`ask_color() <bootstack.ask_color>` and
:class:`ColorChooserDialog <bootstack.dialogs.ColorChooserDialog>` (and its
``ColorChoice`` result) lives on the :doc:`Dialogs </api-reference/dialogs>` API
page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.ask_color
   ~bootstack.dialogs.ColorChooserDialog
   ~bootstack.dialogs.ColorChoice

Full Example
------------

.. literalinclude:: ../../docs/examples/color-dialog.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs