Toast
=====

A temporary notification that floats over the application and auto-dismisses
after a configurable delay.

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/toast-hero-light.png"
        alt="Toast — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/toast-hero-dark.png"
        alt="Toast — dark theme"
        style="max-width:100%;">

Usage
-----

Simple notification
~~~~~~~~~~~~~~~~~~~

Use :func:`bs.toast` for a one-liner that shows and returns immediately.
The toast auto-dismisses after 3 seconds by default.

.. code-block:: python

   bs.toast("Your message here.")
   bs.toast("File saved.", title="Success", accent="success")

With icon
~~~~~~~~~

Pass any Bootstrap Icons name to ``icon=``.

.. code-block:: python

   bs.Toast(
       title="Download complete",
       message="report-2024.pdf was saved.",
       icon="download",
       accent="primary",
       duration=4000,
   ).show()

Accent colors
~~~~~~~~~~~~~

.. code-block:: python

   bs.Toast(title="Success", message="Operation completed.", accent="success").show()
   bs.Toast(title="Warning", message="Disk space low.",      accent="warning").show()
   bs.Toast(title="Error",   message="Upload failed.",       accent="danger").show()
   bs.Toast(title="Info",    message="Update available.",    accent="info").show()

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/toast-accents-light.png"
        alt="Toast accent colors — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/toast-accents-dark.png"
        alt="Toast accent colors — dark theme"
        style="max-width:100%;">

Detail text
~~~~~~~~~~~

``detail`` places a small muted string on the right side of the header row —
useful for timestamps or brief metadata.

.. code-block:: python

   bs.Toast(
       message="Backup completed.",
       detail="just now",
       accent="success",
   ).show()

Action buttons
~~~~~~~~~~~~~~

Pass ``actions`` as a list of button kwarg dicts. Clicking a button dismisses
the toast and passes the dict to ``on_dismiss``.

.. code-block:: python

   bs.Toast(
       title="Delete 3 files?",
       message="This action cannot be undone.",
       accent="danger",
       show_close_button=False,
       actions=[
           {"text": "Cancel"},
           {"text": "Delete", "accent": "danger"},
       ],
       on_dismiss=lambda btn: print("clicked:", btn),
   ).show()

.. raw:: html

   <img class="bs-screenshot-light"
        src="/_static/examples/toast-actions-light.png"
        alt="Toast with action buttons — light theme"
        style="max-width:100%;">
   <img class="bs-screenshot-dark"
        src="/_static/examples/toast-actions-dark.png"
        alt="Toast with action buttons — dark theme"
        style="max-width:100%;">

Dismiss callback
~~~~~~~~~~~~~~~~

``on_dismiss`` fires whenever the toast closes — via the close button,
auto-dismiss timer, or an action button. Action dismissals pass the button's
kwarg dict; all others pass ``None``.

.. code-block:: python

   def on_done(btn):
       if btn and btn.get("text") == "Delete":
           delete_files()

   bs.Toast(title="Delete?", actions=[{"text": "Delete"}],
            on_dismiss=on_done).show()

Duration
~~~~~~~~

Set ``duration`` (milliseconds) for auto-dismiss. Pass ``None`` to keep the
toast visible until the user closes it.

.. code-block:: python

   bs.toast("Visible for 5 seconds.", duration=5000)
   bs.Toast(title="Action required", message="...", duration=None).show()

Programmatic control
~~~~~~~~~~~~~~~~~~~~

Create with :class:`bs.Toast`, then call ``show()`` / ``hide()`` /
``destroy()`` at any time.

.. code-block:: python

   t = bs.Toast(title="Processing…", duration=None)
   t.show()
   # … when done …
   t.hide()

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

Toast class
~~~~~~~~~~~

.. autoclass:: bootstack.widgets.toast.Toast
   :members:
   :undoc-members:

Convenience function
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: bootstack.widgets.toast.toast

Full Example
------------

.. literalinclude:: ../../docs/examples/toast.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
