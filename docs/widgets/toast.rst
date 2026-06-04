Toast
=====

A temporary notification that floats over the application and auto-dismisses
after a configurable delay.

.. image:: /_static/examples/toast-hero-light.png
   :class: bs-screenshot-light
   :alt: Toast — light theme

.. image:: /_static/examples/toast-hero-dark.png
   :class: bs-screenshot-dark
   :alt: Toast — dark theme

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

   bs.Toast(message="Update available", icon="info-circle-fill",          accent="info").show()
   bs.Toast(message="Changes saved",   icon="check-circle-fill",         accent="success").show()
   bs.Toast(message="Storage is low",  icon="exclamation-triangle-fill", accent="warning").show()
   bs.Toast(message="Upload failed",   icon="x-circle-fill",             accent="danger").show()

.. image:: /_static/examples/toast-accents-light.png
   :class: bs-screenshot-light
   :alt: Toast accent colors — light theme

.. image:: /_static/examples/toast-accents-dark.png
   :class: bs-screenshot-dark
   :alt: Toast accent colors — dark theme

Detail text
~~~~~~~~~~~

``detail`` places a small muted string on the right side of the header row —
useful for timestamps or brief metadata.

.. code-block:: python

   bs.Toast(
       message="Backup complete",
       detail="just now",
       accent="success",
   ).show()

.. image:: /_static/examples/toast-detail-light.png
   :class: bs-screenshot-light
   :alt: Toast with detail text — light theme

.. image:: /_static/examples/toast-detail-dark.png
   :class: bs-screenshot-dark
   :alt: Toast with detail text — dark theme

Action buttons
~~~~~~~~~~~~~~

Pass ``actions`` as a list of button kwarg dicts. Clicking a button dismisses
the toast and passes the dict to ``on_dismiss``.

.. code-block:: python

   bs.Toast(
       title="Delete 3 files?",
       message="This action cannot be undone.",
       show_close_button=False,
       actions=[
           {"text": "Cancel"},
           {"text": "Delete", "accent": "danger"},
       ],
       on_dismiss=lambda btn: print("clicked:", btn),
   ).show()

.. image:: /_static/examples/toast-actions-light.png
   :class: bs-screenshot-light
   :alt: Toast with action buttons — light theme

.. image:: /_static/examples/toast-actions-dark.png
   :class: bs-screenshot-dark
   :alt: Toast with action buttons — dark theme

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
