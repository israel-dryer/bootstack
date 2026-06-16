PathField
=========

A text field with a browse button that opens a native file or directory
picker dialog. When the user confirms a selection, the field value is
updated and a ``change`` event fires.

.. image:: /_static/examples/pathfield-hero-light.png
   :class: bs-screenshot-light
   :alt: PathField — light theme

.. image:: /_static/examples/pathfield-hero-dark.png
   :class: bs-screenshot-dark
   :alt: PathField — dark theme

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
       label="Source file",
       placeholder="Select a file…",
       message="Accepted formats: .py, .txt, .csv",
   )
   bs.PathField(
       label="Output directory",
       placeholder="Choose output folder…",
       mode="directory",
       required=True,
   )

.. image:: /_static/examples/pathfield-labels-light.png
   :class: bs-screenshot-light
   :alt: PathField label and message — light theme

.. image:: /_static/examples/pathfield-labels-dark.png
   :class: bs-screenshot-dark
   :alt: PathField label and message — dark theme

States
~~~~~~

.. code-block:: python

   bs.PathField(value="/home/user/docs/report.pdf", label="Normal")
   bs.PathField(value="/home/user/docs/report.pdf", label="Read only", read_only=True)
   bs.PathField(value="/home/user/docs/report.pdf", label="Disabled",  disabled=True)

.. image:: /_static/examples/pathfield-states-light.png
   :class: bs-screenshot-light
   :alt: PathField states — light theme

.. image:: /_static/examples/pathfield-states-dark.png
   :class: bs-screenshot-dark
   :alt: PathField states — dark theme

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

The complete reference for :class:`PathField <bootstack.PathField>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.PathField

Full Example
------------

.. literalinclude:: ../../docs/examples/pathfield.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
