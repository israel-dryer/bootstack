Showing Splash Screens
======================

A splash screen is the borderless intro window your app shows at startup, while
the main window is still being built. bootstack's :class:`~bootstack.Splash` is a
plain container you author like the app body — a logo, a title, a status line —
and the app reveals itself only once the splash dismisses.

This guide walks through the common splash shapes, from a plain intro that covers
startup to a welcome screen that waits for the user, and the one timing rule that
decides which patterns can show live motion.

The mental model
----------------

A splash is its **own window**, not a panel inside the app. Constructing it inside
the ``App`` context registers it automatically; the app then defers showing itself
until the splash dismisses. Because it is a separate window it can appear
*immediately*, so **where you write it decides how much of startup it covers** —
put it first to cover the most.

.. code-block:: python

   import bootstack as bs

   with bs.App(title="My App") as app:
       with bs.Splash(min_duration=1.0):     # appears now
           bs.Picture(logo, width=140, height=140)
           bs.Label("My App", font="heading-lg")

       build_main_window()                   # covered by the splash

   app.run()                                 # app reveals when the splash closes

The ``with`` block scopes content authoring only — leaving it does not close the
splash. What closes it is the ``until`` rule, covered below.

The one timing rule: the event loop must turn
----------------------------------------------

This is the rule that shapes every pattern that follows, so it is worth stating
plainly: **a splash can only show motion while the event loop is running.** The
screen repaints — and a spinner or progress bar advances — only when the loop
gets a turn. The loop is *not* running during the synchronous code between your
``Splash`` block and ``app.run()``.

So the default ``until="ready"`` splash, which covers exactly that synchronous
build, is a **still** image: a logo and a caption, frozen until the app is ready.
That is by design — there is no honest live progress to show for a block of
synchronous work. To show real motion you must hand the loop a turn, which the
patterns below do in two ways: a **timed** splash runs under the live loop, and a
**progress** splash moves the work off the main thread.

A plain intro that covers startup
----------------------------------

The default. ``until="ready"`` closes the splash the moment the app finishes
building. Add ``min_duration`` as an anti-blink floor so a fast startup still
shows the brand for a beat instead of flickering past.

.. code-block:: python

   with bs.App(title="My App") as app:
       with bs.Splash(until="ready", min_duration=1.0):
           bs.Picture(logo, width=140, height=140)
           bs.Label("My App", font="heading-lg")
           bs.Label("Loading…", accent="muted")
       build_main_window()
   app.run()

Keep the content static here — a spinner would sit frozen during the synchronous
build (see the timing rule above).

Timed branding
--------------

Give ``until`` a number of seconds for a splash that shows for a fixed time
regardless of how fast the app builds — a brand moment. App-ready does **not**
cut it short. Because the splash now sits on screen *under the running event
loop* (during ``app.run()``), an indeterminate bar or spinner started with
``start()`` animates here.

.. code-block:: python

   with bs.App(title="My App") as app:
       with bs.Splash(until=2.5):
           bs.Picture(logo, width=140, height=140)
           bs.Label("My App", font="heading-lg")
           bar = bs.ProgressBar(mode="indeterminate")
           bar.start()                       # marches — the loop is live
       build_main_window()
   app.run()

A welcome screen that waits for the user
----------------------------------------

``until="manual"`` never closes on its own. Pair it with ``skippable=True`` (a
click or Escape dismisses it) or an authored button calling
:meth:`~bootstack.Splash.dismiss`. This is the "press any key to continue"
welcome screen.

.. code-block:: python

   with bs.App(title="My App") as app:
       splash = bs.Splash(until="manual")
       with splash:
           bs.Label("Welcome", font="heading-lg")
           bs.Label("Ready when you are.", accent="muted")
           bs.Button("Get started", accent="primary", on_click=splash.dismiss)
   app.run()

Showing real progress
---------------------

For genuine, determinate progress you must move the slow work off the main thread
so the loop stays free to repaint. Run the work in a background thread, push
fractions into a :class:`~bootstack.Signal` the bar is bound to, update a status
label the same way, and call :meth:`~bootstack.Splash.dismiss` when the work is
done. Use ``until="manual"`` so the splash waits for *your* signal, not the
(instant) main-window build.

.. code-block:: python

   import threading
   import bootstack as bs

   with bs.App(title="My App") as app:
       progress = bs.Signal(0.0)
       status = bs.Signal("Starting…")

       splash = bs.Splash(until="manual")
       with splash:
           bs.Picture(logo, width=140, height=140)
           bs.ProgressBar(signal=progress)
           bs.Label(textsignal=status)

       def load():
           steps = ["settings", "plugins", "workspace"]
           for i, step in enumerate(steps):
               status(f"Loading {step}…")
               progress(i / len(steps))
               do_work(step)
           progress(1.0)
           splash.dismiss()                  # close when the real work finishes

       threading.Thread(target=load, daemon=True).start()
   app.run()

Signals marshal updates back to the UI thread, so it is safe to call
``progress(...)`` and ``status(...)`` from the worker. ``dismiss()`` is likewise
safe to call from the thread.

Reacting to dismissal
---------------------

:meth:`~bootstack.Splash.on_dismiss` fires once as the splash begins to close,
with a :class:`~bootstack.events.SplashDismissEvent` whose ``reason`` is
``"ready"``, ``"timer"``, ``"manual"``, or ``"skip"`` — handy for kicking off a
first-run tip or recording that the user skipped the intro.

.. code-block:: python

   splash.on_dismiss(lambda e: print("entered the app via:", e.reason))

The ``min_duration`` floor applies under every pattern: whatever the trigger, the
splash never closes before it elapses.

See also
--------

- :doc:`/widgets/splash` — the widget reference, every option in one place.
- :doc:`/widgets/picture` — display a logo image, crisp on high-DPI displays.
- :doc:`/widgets/progressbar` — the bar used in the timed and progress patterns.
- :doc:`/getting-started/app-structures` — the app shapes a splash introduces.
