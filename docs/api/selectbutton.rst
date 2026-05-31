SelectButton
============

A button that opens a dropdown value list and displays the current selection.

.. code-block:: python

   bs.SelectButton(["Light", "Dark", "Auto"], value="Light")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/selectbutton-light.png"
        alt="SelectButton demo — light theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/selectbutton-dark.png"
        alt="SelectButton demo — dark theme"
        style="max-width:100%; border-radius:10px; margin:1rem 0;">

Usage
-----

Basic
~~~~~

Pass a list of options. The button displays the currently selected value.

.. code-block:: python

   bs.SelectButton(["Light", "Dark", "Auto"], value="Light")

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.SelectButton(["On", "Off"], accent="primary",   value="On")
   bs.SelectButton(["On", "Off"], accent="success",   value="On")
   bs.SelectButton(["On", "Off"], accent="danger",    value="On")

Style variants
~~~~~~~~~~~~~~

.. code-block:: python

   bs.SelectButton(["A", "B", "C"], accent="primary", variant="solid")
   bs.SelectButton(["A", "B", "C"], accent="primary", variant="outline")
   bs.SelectButton(["A", "B", "C"], accent="primary", variant="ghost")

With icon
~~~~~~~~~

.. code-block:: python

   bs.SelectButton(["Light", "Dark", "Auto"],
                   value="Dark", icon="moon-fill")

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal[str]`` with ``signal=``. The button and signal stay in
sync. When ``signal=`` is provided, ``value=`` is ignored — seed the
Signal directly.

.. code-block:: python

   theme = bs.Signal("light")
   bs.SelectButton(["Light", "Dark", "Auto"], signal=theme)
   theme.subscribe(lambda v: bs.set_theme(v.lower()))

Disabled
~~~~~~~~

.. code-block:: python

   bs.SelectButton(["A", "B", "C"], value="B", disabled=True)

Events
~~~~~~

.. code-block:: python

   btn = bs.SelectButton(["Small", "Medium", "Large"], value="Medium")

   btn.on_change(lambda e: print("selected:", btn.value))

   # As a Stream
   btn.on_change().listen(lambda e: apply_size(btn.value))

Programmatic control
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   btn = bs.SelectButton(["A", "B", "C"], value="A")

   btn.value = "C"       # change selection
   btn.disabled = True   # lock the button

API
---

.. autoclass:: bootstack.widgets.selectbutton.SelectButton
   :members:
   :undoc-members:

Full Example
------------

.. literalinclude:: ../../docs/examples/selectbutton.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
