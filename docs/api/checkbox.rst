Checkbox
========

A labelled checkbox for binary on/off input.

.. code-block:: python

   bs.Checkbox("Enable notifications")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/checkbox-light.png"
        alt="Checkbox demo — light theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/checkbox-dark.png"
        alt="Checkbox demo — dark theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">

Usage
-----

Basic
~~~~~

.. code-block:: python

   bs.Checkbox("Accept terms",    value=False)
   bs.Checkbox("Send newsletter", value=True)

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.Checkbox("Primary",   accent="primary",   value=True)
   bs.Checkbox("Secondary", accent="secondary", value=True)
   bs.Checkbox("Info",      accent="info",      value=True)
   bs.Checkbox("Success",   accent="success",   value=True)
   bs.Checkbox("Warning",   accent="warning",   value=True)
   bs.Checkbox("Danger",    accent="danger",    value=True)

Custom state icons
~~~~~~~~~~~~~~~~~~

Use ``on_icon=`` and ``off_icon=`` to show different icons for the checked
and unchecked states. Set ``show_indicator=False`` to replace the box
entirely with the icon pair.

.. code-block:: python

   # Icon replaces the box indicator — shows circle when unchecked,
   # filled check-circle when checked
   bs.Checkbox("Accept",
       on_icon="check-circle-fill", off_icon="circle",
       show_indicator=False, accent="success")

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal`` with ``signal=``. The checkbox and signal stay in sync.
When ``signal=`` is provided, ``value=`` is ignored — seed the Signal
directly.

.. code-block:: python

   agreed = bs.Signal(False)
   bs.Checkbox("I agree to the terms", signal=agreed)
   agreed.subscribe(lambda v: submit_btn.disabled = not v)

Custom values
~~~~~~~~~~~~~

Use ``checked_value=`` and ``unchecked_value=`` when the logical values
are not ``True``/``False``.

.. code-block:: python

   bs.Checkbox("Theme", checked_value="dark", unchecked_value="light")

Tristate
~~~~~~~~

Set ``tristate=True`` to enable a third indeterminate state (dash indicator).
When no ``value=`` is given, the checkbox starts indeterminate. ``value``
returns ``None`` in that state.

.. code-block:: python

   bs.Checkbox("Indeterminate", tristate=True)
   bs.Checkbox("Checked",       tristate=True, value=True)
   bs.Checkbox("Unchecked",     tristate=True, value=False)

   chk = bs.Checkbox("Option", tristate=True)
   print(chk.value)   # → None (indeterminate)
   chk.checked = True
   print(chk.value)   # → True

Disabled
~~~~~~~~

.. code-block:: python

   bs.Checkbox("Cannot change", disabled=True)
   bs.Checkbox("Locked on", value=True, disabled=True)

Events
~~~~~~

.. code-block:: python

   chk = bs.Checkbox("Option")

   # Fires on every toggle
   chk.on_change(lambda e: print("changed:", chk.checked))

   # Fires only when checked
   chk.on_check(lambda e: print("checked"))

   # Fires only when unchecked
   chk.on_uncheck(lambda e: print("unchecked"))

   # As a Stream
   chk.on_change().debounce(200).listen(lambda e: save())

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

.. autoclass:: bootstack.widgets.boolean_controls.Checkbox
   :members:
   :undoc-members:
   :inherited-members: PublicWidgetBase

Full Example
------------

.. literalinclude:: ../../docs/examples/checkbox.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
