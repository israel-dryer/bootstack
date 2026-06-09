Checkbox
========

A labelled checkbox for binary on/off input.

.. image:: /_static/examples/checkbox-tristate-light.png
   :class: bs-screenshot-light
   :alt: Checkbox — light theme

.. image:: /_static/examples/checkbox-tristate-dark.png
   :class: bs-screenshot-dark
   :alt: Checkbox — dark theme

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

.. image:: /_static/examples/checkbox-accents-light.png
   :class: bs-screenshot-light
   :alt: Checkbox accent colors — light theme

.. image:: /_static/examples/checkbox-accents-dark.png
   :class: bs-screenshot-dark
   :alt: Checkbox accent colors — dark theme

Custom state icons
~~~~~~~~~~~~~~~~~~

Use ``on_icon=`` and ``off_icon=`` to show different icons for the checked
and unchecked states. Set ``show_indicator=False`` to replace the box
entirely with the icon pair.

.. code-block:: python

   bs.Checkbox("Checked",
       on_icon="check-circle-fill", off_icon="circle",
       show_indicator=False, accent="success", value=True)
   bs.Checkbox("Unchecked",
       on_icon="check-circle-fill", off_icon="circle",
       show_indicator=False, accent="success", value=False)

.. image:: /_static/examples/checkbox-custom-icons-light.png
   :class: bs-screenshot-light
   :alt: Checkbox custom state icons — light theme

.. image:: /_static/examples/checkbox-custom-icons-dark.png
   :class: bs-screenshot-dark
   :alt: Checkbox custom state icons — dark theme

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

.. image:: /_static/examples/checkbox-tristate-light.png
   :class: bs-screenshot-light
   :alt: Checkbox tristate — light theme

.. image:: /_static/examples/checkbox-tristate-dark.png
   :class: bs-screenshot-dark
   :alt: Checkbox tristate — dark theme

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

Disabled
~~~~~~~~

.. code-block:: python

   bs.Checkbox("Cannot change", disabled=True)
   bs.Checkbox("Locked on", value=True, disabled=True)

.. image:: /_static/examples/checkbox-disabled-light.png
   :class: bs-screenshot-light
   :alt: Checkbox disabled — light theme

.. image:: /_static/examples/checkbox-disabled-dark.png
   :class: bs-screenshot-dark
   :alt: Checkbox disabled — dark theme

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

The complete reference for :class:`Checkbox <bootstack.Checkbox>` lives on the
:doc:`bootstack </api-reference/bootstack>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.Checkbox

Full Example
------------

.. literalinclude:: ../../docs/examples/checkbox.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs