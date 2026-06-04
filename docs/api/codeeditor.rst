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

Basic usage
~~~~~~~~~~~

.. code-block:: python

   bs.CodeEditor()

Syntax highlighting
~~~~~~~~~~~~~~~~~~~

Pass ``language=`` to enable Pygments syntax highlighting. Any Pygments lexer
name is accepted.

.. code-block:: python

   bs.CodeEditor(language="python")
   bs.CodeEditor(language="sql")
   bs.CodeEditor(language="javascript")
   bs.CodeEditor(language="html")

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

   bs.CodeEditor(value=code, language="python", read_only=True)

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

``on_change()`` fires on every edit. Use ``on_input()`` for keystroke-level
feedback.

.. code-block:: python

   editor = bs.CodeEditor(language="python")

   editor.on_change(lambda e: autosave(editor.value))

   # Debounced Stream — save 500ms after the last keystroke
   editor.on_change().debounce(500).listen(lambda e: autosave(editor.value))

Cursor position
~~~~~~~~~~~~~~~

``on_cursor_move()`` fires after any key press or mouse click that moves the
insertion cursor.

.. code-block:: python

   editor = bs.CodeEditor(language="python")

   def show_pos(e):
       idx = editor._internal._core.text.index("insert")
       line, col = idx.split(".")
       status.text = f"Ln {line}, Col {int(col) + 1}"

   editor.on_cursor_move(show_pos)

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

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

See also
--------

* :doc:`textarea` — plain multi-line text input for form fields

API
---

.. autoclass:: bootstack.widgets.codeeditor.CodeEditor
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: tk

Full Example
------------

.. literalinclude:: ../../docs/examples/codeeditor.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs