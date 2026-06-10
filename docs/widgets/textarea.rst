TextArea
========

A multi-line text input with optional label, placeholder, scrollbars, and
undo/redo support.

.. image:: /_static/examples/textarea-hero-light.png
   :class: bs-screenshot-light
   :alt: TextArea — light theme

.. image:: /_static/examples/textarea-hero-dark.png
   :class: bs-screenshot-dark
   :alt: TextArea — dark theme

Usage
-----

Basic usage
~~~~~~~~~~~

.. code-block:: python

   bs.TextArea(placeholder="Start typing…")

Height
~~~~~~

Use ``height=`` to set the visible row count (default ``4``).

.. code-block:: python

   bs.TextArea(height=6)

Label and message
~~~~~~~~~~~~~~~~~

Use ``label=`` for a field title and ``message=`` for helper text below.

.. code-block:: python

   bs.TextArea(
       label="Description",
       message="Markdown supported.",
       placeholder="Write a short description…",
       height=4,
   )

Max length
~~~~~~~~~~

Set ``max_length=`` to cap the number of characters the user can type.

.. code-block:: python

   bs.TextArea(
       label="Bio",
       placeholder="Tell us about yourself…",
       max_length=200,
       message="Maximum 200 characters.",
   )

Scrollbars
~~~~~~~~~~

Control when scrollbars appear with ``scrollbars=``. The default ``'auto'``
shows scrollbars only when content overflows.

.. code-block:: python

   bs.TextArea(scrollbars="auto")      # default — appears on overflow
   bs.TextArea(scrollbars="vertical")  # always visible
   bs.TextArea(scrollbars="both")      # horizontal + vertical, always
   bs.TextArea(scrollbars="none")      # never shown

.. image:: /_static/examples/textarea-scrollbars-light.png
   :class: bs-screenshot-light
   :alt: TextArea scrollbars — light theme

.. image:: /_static/examples/textarea-scrollbars-dark.png
   :class: bs-screenshot-dark
   :alt: TextArea scrollbars — dark theme

States
~~~~~~

.. code-block:: python

   bs.TextArea(value="Editable content.",  label="Normal")
   bs.TextArea(value="Read-only content.", label="Read only", read_only=True)

.. image:: /_static/examples/textarea-states-light.png
   :class: bs-screenshot-light
   :alt: TextArea states — light theme

.. image:: /_static/examples/textarea-states-dark.png
   :class: bs-screenshot-dark
   :alt: TextArea states — dark theme

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal[str]`` with ``textsignal=``. The field and signal stay in
sync automatically.

.. code-block:: python

   content = bs.Signal("")
   bs.TextArea(label="Notes", textsignal=content)
   bs.Label(textsignal=content, accent="secondary")

Handling changes
~~~~~~~~~~~~~~~~

Use ``on_input()`` for real-time keystroke feedback or ``on_change()`` for
commit-on-blur behaviour (fires when the user leaves the field).

.. code-block:: python

   ta = bs.TextArea(label="Notes")

   # Fires on every edit
   ta.on_input(lambda e: print(len(ta.value), "chars"))

   # Fires on blur
   ta.on_change(lambda e: save(ta.value))

   # As a debounced Stream
   ta.on_input().debounce(500).listen(lambda e: autosave(ta.value))

Undo and redo
~~~~~~~~~~~~~

TextArea maintains a built-in undo/redo stack. Call ``undo()`` and ``redo()``
programmatically, or let the user use Ctrl+Z / Ctrl+Y.

.. code-block:: python

   ta = bs.TextArea()
   bs.Button("Undo", on_click=lambda: ta.undo())
   bs.Button("Redo", on_click=lambda: ta.redo())

Dirty tracking
~~~~~~~~~~~~~~

``is_dirty`` is ``True`` after any edit since the last ``mark_saved()`` call.
Use it to show unsaved-change indicators.

.. code-block:: python

   ta = bs.TextArea()
   ta.on_modified(lambda e: print("dirty:", ta.is_dirty))

   # After saving
   ta.mark_saved()

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`textfield` — single-line text input
* :doc:`codeeditor` — syntax-highlighted code editor

API
---

The complete reference for :class:`TextArea <bootstack.TextArea>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.TextArea

Full Example
------------

.. literalinclude:: ../../docs/examples/textarea.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs