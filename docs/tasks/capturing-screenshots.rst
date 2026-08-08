Capturing Screenshots
=====================

Every widget can save a picture of itself. Call ``capture()`` on the app to get
the whole window, or on a single widget to get just that part of it — useful for
letting someone share a dashboard, a report, or one chart with a colleague who
does not have the application.

.. code-block:: python

   import bootstack as bs

   with bs.App(title="Dashboard") as app:
       bs.Label("Quarterly numbers", font="heading-lg")
       bs.Button("Save a picture", on_click=lambda: app.capture("dashboard.png"))
   app.run()

The one thing to understand up front: a capture reads pixels from the display.
It photographs what is actually on screen rather than re-rendering the interface
offscreen, so the widget has to be visible. The window is brought to the front
automatically before the picture is taken.

Letting the user choose the file
--------------------------------

In practice you rarely want a hard-coded filename. Pair the capture with
:func:`~bootstack.ask_save_file` and the user picks both the location and the
format:

.. code-block:: python

   def on_export():
       chosen = bs.ask_save_file(
           initial_file="dashboard.png",
           file_types=[("PNG image", "*.png"),
                       ("JPEG image", "*.jpg"),
                       ("PDF document", "*.pdf")],
       )
       if chosen:
           app.capture(chosen)

   bs.Button("Export…", accent="primary", on_click=on_export)

That is the whole feature for most applications — a button, a save dialog, and
one call.

Capturing part of the window
----------------------------

Call ``capture()`` on any widget to photograph only that widget. Give the piece
you want to export a name and capture it directly:

.. code-block:: python

   with bs.Card(padding=12) as summary:
       bs.Label("Revenue", font="heading-md")
       bs.Label("$1.2M")

   bs.Button("Share this card", on_click=lambda: summary.capture("revenue.png"))

Capturing a whole window often catches a one-pixel border artifact from the
native window frame. Trim it with ``inset``, which shaves that many pixels off
every edge:

.. code-block:: python

   app.capture("window.png", inset=2)

Choosing the format
-------------------

The file extension selects the format — there is no separate argument for it.
``.png`` is the right default for interface captures because it stores the
pixels exactly. ``.jpg`` produces a smaller file at some cost in sharpness,
which is noticeable on text and thin lines. ``.pdf`` writes the capture as a
single-page document, which is convenient when the picture is going to be
printed or attached to a report.

.. code-block:: python

   app.capture("report.pdf")

Missing folders in the path are created for you, and the method returns the path
it wrote, so it composes with whatever comes next:

.. code-block:: python

   written = app.capture("exports/2026/q1.png")
   bs.toast(f"Saved to {written}")

What a capture cannot do
------------------------

Because a capture photographs the screen, a few things follow that are worth
knowing before you build on it:

- **The widget must be on screen.** Capturing a hidden or detached widget raises
  an error rather than silently saving whatever happened to be behind it.
- **Anything covering the widget is captured with it.** The window is raised
  first, which handles the ordinary case, but a window pinned always-on-top by
  another application still lands in the picture.
- **The capture is what the screen shows.** A long list scrolled halfway down is
  captured halfway down; there is no way to photograph content scrolled out of
  view. Capturing a widget that has been scrolled right out of its viewport
  raises an error rather than photographing whatever now sits in its place — a
  row still counts as capturable while any part of it is in view.
- **On a Retina Mac the picture is saved at the window's own size.** A 560×360
  window produces a 560×360 image rather than the finer pixel grid the display
  actually draws it on, so text is slightly softer than in a screenshot taken
  with the system's own tool. Captures come out the same size on every machine,
  which is usually what you want when they are headed for a report.
- **On macOS, the application needs permission to record the screen.** Without it
  the system quietly hands back a picture of the desktop instead of the window —
  no error, just the wrong image. macOS asks the first time an application
  captures anything and never asks again if that prompt was declined; grant it
  under System Settings → Privacy and Security → Screen and System Audio
  Recording (called Screen Recording before macOS 15) and restart the
  application. While developing, the permission follows whatever launched the
  script, so it is the terminal or editor that needs it rather than the script
  itself.
- **On Linux, a Wayland session may need a screenshot helper installed.** An X11
  session captures directly and needs nothing. Wayland does not let an
  application read the screen for itself, so the capture goes through the
  desktop's own screenshot tool — ``grim`` on Sway and other wlroots desktops,
  ``spectacle`` on KDE, ``gnome-screenshot`` where it is still present. Some
  desktops ship none of them, and there the capture raises an error naming what
  to install rather than saving anything. Worth checking early if your users are
  on Linux, because it is the one platform where capture can be unavailable
  outright.

If the application already had its window pinned always-on-top, that setting is
left exactly as it was found.

Printing
--------

There is deliberately no print method. Handing a file to the operating system's
printer works very differently on each platform, and on Windows the only
available route cannot be told which printer to use or how many copies to run —
so the arguments would be there but ignored. Saving the capture and letting the
user print it from an application built for printing is more dependable. A
``.pdf`` capture is usually the most convenient thing to hand them.

See also
--------

- :doc:`/tasks/dialogs` — the save dialog used above, and the rest of the dialog
  verbs.
- :doc:`/reference/images` — displaying images inside the interface, including
  showing a capture back to the user.
