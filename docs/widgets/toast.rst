Toasts & Notifications
======================

bootstack has three transient message surfaces, each for a distinct job:

- :func:`bs.toast() <bootstack.toast>` — a **passive** message that fades on its
  own, in a screen corner.
- :class:`bs.Notification <bootstack.Notification>` — a **persistent** corner
  message the user closes.
- :class:`bs.Snackbar <bootstack.Snackbar>` — an **in-app** message with a single
  action, at the window's bottom edge.

They share one look (a compact card with an icon, message, and severity color)
but differ in *where* they sit, *how long* they stay, and *whether* they ask for
a response. Pick by the job, not the appearance.

Choosing a surface
------------------

.. list-table::
   :header-rows: 1
   :widths: 18 28 18 18 18

   * - Surface
     - Use it for
     - Lifetime
     - Anchored to
     - Action
   * - ``toast()``
     - "FYI" that needs no response (*Saved*, *Copied*)
     - Auto-dismiss
     - A monitor corner
     - None
   * - ``Notification``
     - News that should wait to be seen (*Backup finished*)
     - Until closed
     - A monitor corner
     - Close only
   * - ``Snackbar``
     - Feedback on an action just taken, maybe reversible
     - Auto-dismiss
     - The window's bottom
     - One (*Undo*)

A rule of thumb: reach for ``toast()`` first. Upgrade to ``Notification`` when
the message must persist, and to ``Snackbar`` when it offers a single response.
Anything that *blocks* the user until answered is a dialog
(:doc:`/tasks/dialogs`), not a message.

Toast
-----

:func:`bs.toast() <bootstack.toast>` shows a message and returns immediately — it
is fire-and-forget. It floats in a corner of the monitor the app window is on,
stacks under any toasts already there, and fades after ``duration``. There is no
close button: a toast is passive by definition.

At its simplest a toast is just its message on one line. The icon and the title
are both optional — add an icon to lead the message, or a title for a two-line
card:

.. code-block:: python

   bs.toast("Your changes were saved.")                          # message only
   bs.toast("Battery at 12%.", icon="battery-half", accent="warning")  # icon + message
   bs.toast("Could not reach the server.", title="Sync failed",  # title + message
            accent="danger")

.. image:: /_static/examples/toast-hero-light.png
   :class: bs-screenshot-light
   :alt: A passive toast in a corner — light theme

.. image:: /_static/examples/toast-hero-dark.png
   :class: bs-screenshot-dark
   :alt: A passive toast in a corner — dark theme

The accent colors the icon and text (in a readable, dark-tinted shade) and gives
the card a soft tint; omit it for a neutral toast. ``corner=`` overrides the
default placement (bottom-right, top-right on Linux):

.. code-block:: python

   bs.toast("Pinned to the top-left.", corner="top-left", duration=6000)

Notification
------------

:class:`bs.Notification <bootstack.Notification>` is the persistent sibling: same
corner, same stacking, but it does **not** auto-dismiss. It carries a close
button and stays until the user dismisses it or your code does. Build it, then
``show()`` — keep the handle if you want to ``dismiss()`` it later (e.g. when a
job it announced is superseded). The title is the headline:

.. code-block:: python

   note = bs.Notification(
       "Backup complete",
       message="3.2 GB uploaded to the cloud.",
       detail="just now",
       icon="cloud-check",
       accent="success",
   ).show()

   # later, when it no longer applies
   note.dismiss()

.. image:: /_static/examples/toast-notification-light.png
   :class: bs-screenshot-light
   :alt: A persistent notification with a close button — light theme

.. image:: /_static/examples/toast-notification-dark.png
   :class: bs-screenshot-dark
   :alt: A persistent notification with a close button — dark theme

A notification is message-only — it informs, it does not ask. If you need the
user to *do* something, that is a snackbar action or a dialog.

Snackbar
--------

:class:`bs.Snackbar <bootstack.Snackbar>` belongs to the app, not the screen: it
sits at the bottom edge of the window and moves with it. It is for brief feedback
on something that just happened, optionally with a single way to respond — the
classic *"Message archived. [Undo]"*. Only one snackbar shows at a time; a new
one replaces it. Use the :func:`bs.snackbar() <bootstack.snackbar>` verb for the
common one-liner, or the class when you want to ``dismiss()`` it yourself:

.. code-block:: python

   bs.snackbar("Conversation archived.", action="Undo", on_action=restore)
   bs.snackbar("Copied to clipboard.")                       # no action

.. image:: /_static/examples/toast-snackbar-light.png
   :class: bs-screenshot-light
   :alt: A snackbar with an Undo action at the window bottom — light theme

.. image:: /_static/examples/toast-snackbar-dark.png
   :class: bs-screenshot-dark
   :alt: A snackbar with an Undo action at the window bottom — dark theme

The action fires ``on_action`` and then dismisses. Unlike a toast, a snackbar's
surface stays neutral — severity coloring is the corner surfaces' job; the
``accent`` here only tints the action button. ``align=`` moves it along the
bottom edge (``'left'``, ``'center'``, or ``'right'``).

Reacting to dismissal
---------------------

All three take an ``on_dismiss`` callback, fired with no arguments whenever the
message goes away — by timeout, the close button, the snackbar action, or a
manual ``dismiss()``:

.. code-block:: python

   bs.toast("Synced.", on_dismiss=lambda: print("gone"))

Widget sizing
~~~~~~~~~~~~~

.. include:: ../shared/widget-sizing.rst

API
---

The verbs and classes live on the :doc:`Widgets </api-reference/widgets>` API
page. At a glance:

.. autosummary::
   :nosignatures:

   ~bootstack.toast
   ~bootstack.Notification
   ~bootstack.Snackbar
   ~bootstack.snackbar

Full Example
------------

.. literalinclude:: ../../docs/examples/toast.py
   :language: python
   :linenos:
   :start-after: import bootstack as bs
