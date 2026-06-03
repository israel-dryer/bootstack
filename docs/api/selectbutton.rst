SelectButton
============

A button that opens a dropdown value list and displays the current selection.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/selectbutton-hero-light.png"
        alt="SelectButton — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/selectbutton-hero-dark.png"
        alt="SelectButton — dark theme"
        style="max-width:100%;">

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

   bs.SelectButton(["Primary"],   accent="primary",   value="Primary")
   bs.SelectButton(["Secondary"], accent="secondary", value="Secondary")
   bs.SelectButton(["Info"],      accent="info",      value="Info")
   bs.SelectButton(["Success"],   accent="success",   value="Success")
   bs.SelectButton(["Warning"],   accent="warning",   value="Warning")
   bs.SelectButton(["Danger"],    accent="danger",    value="Danger")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/selectbutton-accents-light.png"
        alt="SelectButton accent colors — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/selectbutton-accents-dark.png"
        alt="SelectButton accent colors — dark theme"
        style="max-width:100%;">

Style variants
~~~~~~~~~~~~~~

.. code-block:: python

   bs.SelectButton(["Solid"],   accent="primary", variant="solid")
   bs.SelectButton(["Outline"], accent="primary", variant="outline")
   bs.SelectButton(["Ghost"],   accent="primary", variant="ghost")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/selectbutton-variants-light.png"
        alt="SelectButton style variants — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/selectbutton-variants-dark.png"
        alt="SelectButton style variants — dark theme"
        style="max-width:100%;">

With icon
~~~~~~~~~

.. code-block:: python

   bs.SelectButton(["Light", "Dark", "Auto"],
                   value="Dark", icon="moon-fill")
   bs.SelectButton(["Small", "Medium", "Large"],
                   value="Large", icon="fonts", accent="secondary")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/selectbutton-icon-light.png"
        alt="SelectButton with icon — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/selectbutton-icon-dark.png"
        alt="SelectButton with icon — dark theme"
        style="max-width:100%;">

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
   bs.SelectButton(["A", "B", "C"], value="B", disabled=True,
                   accent="primary", variant="outline")

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/selectbutton-disabled-light.png"
        alt="SelectButton disabled — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/selectbutton-disabled-dark.png"
        alt="SelectButton disabled — dark theme"
        style="max-width:100%;">

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

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

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