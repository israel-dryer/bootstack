CodeEditor
==========

A full-featured code editor with syntax highlighting, line numbers, bracket
matching, smart indent, and built-in search/replace.

.. image:: /_static/examples/codeeditor-hero-light.png
   :class: bs-screenshot-light
   :alt: CodeEditor — light theme

.. image:: /_static/examples/codeeditor-hero-dark.png
   :class: bs-screenshot-dark
   :alt: CodeEditor — dark theme

Usage
-----

Think of it as a standalone editing *surface*, not a form input: it ships the
editor behaviors (a gutter, a search bar, undo grouping) built in, and it is
**not** Field-wrapped — there is no label, validation, or ``disabled`` state.
Reach for :doc:`textarea` when you want a labeled multi-line field in a form.

Basic usage
~~~~~~~~~~~

.. code-block:: python

   bs.CodeEditor()

Syntax highlighting
~~~~~~~~~~~~~~~~~~~

Pass ``language=`` to enable Pygments syntax highlighting. Any Pygments lexer
name is accepted.

.. code-block:: python

   bs.CodeEditor(value=python_source, language="python")
   bs.CodeEditor(value=sql_source,    language="sql")
   # Any Pygments lexer name works — "javascript", "html", "yaml", …

.. image:: /_static/examples/codeeditor-languages-light.png
   :class: bs-screenshot-light
   :alt: CodeEditor languages — light theme

.. image:: /_static/examples/codeeditor-languages-dark.png
   :class: bs-screenshot-dark
   :alt: CodeEditor languages — dark theme

Color themes
~~~~~~~~~~~~

By default (``theme='auto'``), the editor switches between ``light_theme``
and ``dark_theme`` to match the active bootstack theme. Pass an explicit
Pygments style name to pin the scheme.

.. code-block:: python

   bs.CodeEditor(language="python", theme="auto")           # follows app theme
   bs.CodeEditor(language="python", theme="monokai")        # always dark
   bs.CodeEditor(language="python", theme="default")        # always light
   bs.CodeEditor(language="python",
                 light_theme="friendly",
                 dark_theme="dracula")                      # custom pair

Read-only state
~~~~~~~~~~~~~~~

.. code-block:: python

   bs.CodeEditor(value=code, language="python")                   # editable
   bs.CodeEditor(value=code, language="python", read_only=True)   # read-only

Read-only blocks *typing*, not programmatic edits: ``editor.value = ...``,
``editor.insert(...)``, and ``editor.clear()`` all still apply, leaving the
editor read-only afterward.

.. image:: /_static/examples/codeeditor-states-light.png
   :class: bs-screenshot-light
   :alt: CodeEditor states — light theme

.. image:: /_static/examples/codeeditor-states-dark.png
   :class: bs-screenshot-dark
   :alt: CodeEditor states — dark theme

Editor options
~~~~~~~~~~~~~~

.. code-block:: python

   bs.CodeEditor(
       language="python",
       tab_width=4,           # spaces per tab stop (default 4)
       insert_spaces=True,    # Tab inserts spaces (default True)
       auto_indent=True,      # match indentation on Return (default True)
       show_line_numbers=True,  # line-number gutter (default True)
       show_indent_guides=False,  # vertical guide marks (default False)
       wrap=False,            # horizontal scroll (default; True to wrap)
   )

Handling changes
~~~~~~~~~~~~~~~~

``on_change()`` fires on every edit, delivering a
:class:`~bootstack.events.ChangeEvent` whose ``value`` is the editor text. Use
``on_input()`` for keystroke-level feedback before the change is committed. See
:doc:`/reference/events` for the full event model.

.. code-block:: python

   editor = bs.CodeEditor(language="python")

   editor.on_change(lambda e: autosave(editor.value))

   # Debounced Stream — save 500ms after the last keystroke
   editor.on_change().debounce(500).listen(lambda e: autosave(editor.value))

Cursor position
~~~~~~~~~~~~~~~

``on_cursor_move()`` fires after any key press or mouse click that moves the
insertion cursor. Read ``cursor_position`` — a 1-indexed ``(line, column)``
tuple — to drive a status-bar readout.

.. code-block:: python

   editor = bs.CodeEditor(language="python")

   def show_pos(e):
       line, col = editor.cursor_position
       status.text = f"Ln {line}, Col {col}"

   editor.on_cursor_move(show_pos)

Text positions
~~~~~~~~~~~~~~

Methods that take a position — ``insert()`` and ``goto_line()`` — address it
two ways:

* ``"end"`` — just past the last character.
* ``"line.column"`` — a line and column, for example ``"1.0"`` for the very
  start or ``"3.4"`` for line 3 just after its fourth character. **Lines are
  1-indexed; columns are 0-indexed**, so column ``0`` is the start of a line.

.. code-block:: python

   editor.insert("end", "\n# appended")   # add a trailing line
   editor.insert("1.0", "#!/usr/bin/env python\n")  # prepend a shebang
   editor.goto_line(42)                   # jump to line 42 (1-indexed)

.. note::

   ``cursor_position`` reports a **1-indexed** ``(line, column)`` tuple — column
   ``1`` is the start of a line — because it is meant for a status-bar readout
   (``Ln 1, Col 1``). That display convention differs from the **0-indexed**
   column in a ``"line.column"`` address: the cursor at the very start reads
   ``(1, 1)`` but is inserted at by ``"1.0"``.

Undo and redo
~~~~~~~~~~~~~

The editor maintains a built-in undo/redo stack. Use ``undo_block()`` to
group multiple programmatic edits into a single undo step.

.. code-block:: python

   editor = bs.CodeEditor(language="python")
   editor.undo()
   editor.redo()

   # Group edits into one undo step
   with editor.undo_block():
       editor.insert("1.0", "# Auto-generated\\n")
       editor.value = reformatted

Dirty tracking
~~~~~~~~~~~~~~

``is_dirty`` is ``True`` after any edit since the last ``mark_saved()`` call.

.. code-block:: python

   editor = bs.CodeEditor(language="python")
   editor.on_modified(lambda e: update_title(editor.is_dirty))

   # After saving
   editor.mark_saved()

Search and replace
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   editor.show_search()   # open find bar
   editor.show_replace()  # open find/replace bar
   editor.hide_search()   # close the bar

Keyboard
~~~~~~~~

The editor uses editor-grade key bindings rather than form-field traversal.
Undo and redo bind to the platform's native shortcuts (``Ctrl+Z`` / ``Ctrl+Y``
on Windows and Linux, ``Cmd+Z`` / ``Cmd+Shift+Z`` on macOS).

============================  ============================================================
Key                           Action
============================  ============================================================
``Tab``                       Insert indentation to the next tab stop
``Return``                    New line, matching the current indent (``auto_indent``)
Undo / redo                   Native per-platform shortcut (see above)
``Ctrl+F`` / ``Cmd+F``        Open the find bar
``Ctrl+H`` / ``Cmd+H``        Open the find/replace bar
``Escape``                    Close the find/replace bar
============================  ============================================================

.. note::

   ``Tab`` inserts indentation, so it does not move focus out of the editor —
   that is deliberate for a code surface, matching desktop editors. Move focus
   away by clicking another control. When you instead want a labeled multi-line
   field where ``Tab`` advances focus, use :doc:`textarea`.

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`textarea` — plain multi-line text input for form fields

API
---

The complete reference for :class:`CodeEditor <bootstack.CodeEditor>` lives on the
:doc:`Widgets </api-reference/widgets>` API page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.CodeEditor

Full Example
------------

.. literalinclude:: ../../docs/examples/codeeditor.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs