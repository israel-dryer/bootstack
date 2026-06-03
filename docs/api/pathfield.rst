PathField
=========

A text field with a browse button that opens a native file or directory
picker dialog. When the user confirms a selection, the field value is
updated and a ``change`` event fires.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/pathfield-hero-light.png"
        alt="PathField — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/pathfield-hero-dark.png"
        alt="PathField — dark theme" style="max-width:100%;">

Usage
-----

Basic usage
~~~~~~~~~~~

.. code-block:: python

   bs.PathField(placeholder="Select a file…")

Dialog modes
~~~~~~~~~~~~

Use ``mode=`` to control which native dialog opens when the browse button is
clicked. The default is ``'open'``.

.. code-block:: python

   bs.PathField(mode="open")           # single-file open
   bs.PathField(mode="open_multiple")  # multi-file open (result is a tuple)
   bs.PathField(mode="save")           # save-file dialog
   bs.PathField(mode="directory")      # directory picker

File filters
~~~~~~~~~~~~

Pass ``file_filters=`` as a list of ``(description, pattern)`` pairs to
restrict which file types appear in the dialog. Has no effect in
``'directory'`` mode.

.. code-block:: python

   bs.PathField(
       file_filters=[
           ("Images", "*.png *.jpg *.jpeg *.gif"),
           ("All Files", "*.*"),
       ],
   )

Label and message
~~~~~~~~~~~~~~~~~

Use ``label=`` for a field title and ``message=`` for helper text below.
Set ``required=True`` to mark the field visually.

.. code-block:: python

   bs.PathField(
       label="Output directory",
       message="Folder must be writable.",
       mode="directory",
       required=True,
   )

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/pathfield-labels-light.png"
        alt="PathField label and message — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/pathfield-labels-dark.png"
        alt="PathField label and message — dark theme" style="max-width:100%;">

States
~~~~~~

.. code-block:: python

   bs.PathField(value="/home/user/docs/report.pdf", label="Normal")
   bs.PathField(value="/home/user/docs/report.pdf", label="Read only", read_only=True)
   bs.PathField(value="/home/user/docs/report.pdf", label="Disabled",  disabled=True)

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/pathfield-states-light.png"
        alt="PathField states — light theme" style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/pathfield-states-dark.png"
        alt="PathField states — dark theme" style="max-width:100%;">

Reactive binding
~~~~~~~~~~~~~~~~

Bind a ``Signal[str]`` with ``textsignal=``. The field and signal stay in
sync automatically.

.. code-block:: python

   path = bs.Signal("")
   bs.PathField(label="Pick a file", textsignal=path)
   bs.Label(textsignal=path, accent="secondary")   # updates on each selection

Handling changes
~~~~~~~~~~~~~~~~

Use ``on_change()`` to respond when the user picks a path. The event fires
after the dialog closes and the value is committed, or when the user edits the
text portion directly and leaves the field.

.. code-block:: python

   pf = bs.PathField(label="Source file")

   def handle_change(e):
       print("Selected:", pf.value)

   pf.on_change(handle_change)

   # As a subscription (cancellable)
   sub = pf.on_change(handle_change)
   sub.cancel()

   # As a Stream (composable)
   pf.on_change().listen(handle_change)

For ``'open_multiple'`` mode, the raw tuple of paths is available on
``pf.dialog_result`` after the dialog closes.

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`textfield` — plain single-line text input
* :doc:`numberfield` — numeric-only input with stepper

API
---

.. autoclass:: bootstack.widgets.pathfield.PathField
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: tk

Full Example
------------

.. literalinclude:: ../../docs/examples/pathfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
