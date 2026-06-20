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

A path field is a text input with a browse button. ``field.value`` is the
selected path as a string — the user types it or picks it from a native dialog,
and ``mode`` chooses which dialog opens (open a file, open many, save, or pick a
directory). ``on_change`` fires after a pick or a manual edit; in
``'open_multiple'`` mode the raw tuple of paths is on ``field.dialog_result``.

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

Validation
~~~~~~~~~~

A path field validates like any text field — rules run against the path
**string**. Attach them with ``add_validation_rule()`` (for example a ``custom``
rule that checks the extension, or ``required`` for a mandatory path):

.. code-block:: python

   field = bs.PathField(label="Data file")
   field.add_validation_rule(
       "custom",
       func=lambda path: bool(path) and path.endswith(".csv"),
       message="Choose a .csv file.",
       trigger="blur",
   )

   is_valid = field.validate()   # run every rule on demand

.. image:: /_static/examples/pathfield-validation-light.png
   :class: bs-screenshot-light
   :alt: PathField validation — light theme

.. image:: /_static/examples/pathfield-validation-dark.png
   :class: bs-screenshot-dark
   :alt: PathField validation — dark theme

Validity is reactive state. ``field.valid`` is a ``Signal[bool]`` and
``field.error`` a ``Signal[str]`` (the current message, ``""`` when valid) — bind
the error straight to a label and it keeps itself in sync:

.. code-block:: python

   bs.Label(textsignal=field.error, accent="danger")   # shows and clears itself

.. note::

   The full rule taxonomy and aggregating a whole form's validity live in the
   :doc:`Validation </reference/validation>` guide.

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`textfield` — plain single-line text input
* :doc:`numberfield` — numeric-only input with stepper
* :doc:`Validation </reference/validation>` — the full rule set and form-level validity
* :doc:`Composing Fields </tasks/composing-fields>` — add buttons or icons inside a field
* :doc:`Signals </reference/signals>` — the reactive binding behind ``textsignal=``

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
