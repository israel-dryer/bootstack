Switch
======

A sliding track-and-thumb toggle for binary on/off input.

.. code-block:: python

   bs.Switch("Dark mode")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/switch-light.png"
        alt="Switch demo — light theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/switch-dark.png"
        alt="Switch demo — dark theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">

Usage
-----

Basic
~~~~~

.. code-block:: python

   bs.Switch("Off", value=False)
   bs.Switch("On",  value=True)

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.Switch("Primary",   accent="primary",   value=True)
   bs.Switch("Secondary", accent="secondary", value=True)
   bs.Switch("Info",      accent="info",      value=True)
   bs.Switch("Success",   accent="success",   value=True)
   bs.Switch("Warning",   accent="warning",   value=True)
   bs.Switch("Danger",    accent="danger",    value=True)

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal`` with ``signal=``. The switch and signal stay in sync.
When ``signal=`` is provided, ``value=`` is ignored — seed the Signal
directly.

.. code-block:: python

   dark_mode = bs.Signal(False)
   bs.Switch("Dark mode", signal=dark_mode)
   dark_mode.subscribe(lambda v: bs.set_theme("dark" if v else "light"))

Custom values
~~~~~~~~~~~~~

Use ``checked_value=`` and ``unchecked_value=`` when the logical values
are not ``True``/``False``.

.. code-block:: python

   bs.Switch("Theme",
       checked_value="dark",
       unchecked_value="light",
       value="light")

Disabled
~~~~~~~~

.. code-block:: python

   bs.Switch("Cannot change", disabled=True)
   bs.Switch("Locked on",     value=True, disabled=True)

Events
~~~~~~

.. code-block:: python

   sw = bs.Switch("Notifications")

   # Fires on every toggle
   sw.on_change(lambda e: print("changed:", sw.checked))

   # Fires only when switched on
   sw.on_check(lambda e: print("switched on"))

   # Fires only when switched off
   sw.on_uncheck(lambda e: print("switched off"))

   # As a Stream
   sw.on_change().debounce(200).listen(lambda e: save_settings())

Programmatic control
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   sw = bs.Switch("Option")

   sw.checked = True          # turn on
   sw.value                   # → True
   sw.toggle()                # flip state

   sw.disabled = True         # lock the switch

API
---

.. autoclass:: bootstack.widgets.boolean_controls.Switch
   :members:
   :undoc-members:
   :inherited-members: PublicWidgetBase

Full Example
------------

.. literalinclude:: ../../docs/examples/switch.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
