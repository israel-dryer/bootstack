"""Hero screenshots for the Toasts & Notifications guide.

One card per scene, captured directly via app._capture_target. Each card is
placed over the (topmost) app window so the small capture pad picks up a clean
neutral backdrop rather than the desktop. The internal engine is used so the
scene can position each card and grab its Toplevel; the rendered cards are
identical to the public toast() / Notification / Snackbar surfaces.

Regenerate with::

    py -3.12 docs/scripts/take_screenshots.py toast
"""
import bootstack as bs
from bootstack.widgets._impl.composites.toast import Toast as _Toast

# The runner places the app at +200+100; sit the card just inside it.
_POS = "+230+150"


def _scene(name, size, **toast_kwargs):
    with bs.App(title=name, size=size, padding=0) as app:
        def show():
            t = _Toast(duration=9000, position=_POS, **toast_kwargs)
            t.show()
            app._capture_target = t._toplevel
        # Show after the runner lifts the app to topmost (t=800) so the card,
        # also topmost, sits above it; grab follows at t=950.
        app.tk.after(850, show)
    app.run()


def hero():
    # A passive toast — single line: icon + message, no title, no close button.
    _scene(
        "toast", (440, 160),
        message="Your changes were saved.",
        icon="check-circle-fill",
        accent="success",
        show_close_button=False,
    )


def notification():
    # Persistent — close button + muted detail.
    _scene(
        "notification", (440, 200),
        title="Backup complete",
        message="3.2 GB uploaded to the cloud.",
        memo="just now",
        icon="cloud-check",
        accent="success",
        show_close_button=True,
    )


def snackbar():
    # Neutral surface + a single ghost action (matches the public Snackbar).
    _scene(
        "snackbar", (440, 160),
        message="Conversation archived.",
        icon="",
        show_close_button=False,
        buttons=[{"text": "Undo", "variant": "ghost", "accent": "primary"}],
    )


SCENES = {
    "hero": hero,
    "notification": notification,
    "snackbar": snackbar,
}
