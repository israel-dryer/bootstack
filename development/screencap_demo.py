"""Live demo for `screencap.py` — capture the screen or this window, and
show the result immediately.

Each capture is written to `development/screencap_out/` and then displayed
in the preview area below the buttons, so you can see what was grabbed
without leaving the app.

Deferred work goes through `widget.schedule` (`delay`/`every`), the public
scheduling API — its jobs are cancelled automatically when the widget is
destroyed.

Run: py -3.12 development/screencap_demo.py
"""

from pathlib import Path

import bootstack as bs

from screencap import (capture_monitor, capture_screen, capture_widget,
                       list_monitors, monitor_for_widget)

OUT = Path(__file__).parent / "screencap_out"


def on_all_monitors():
    """Grab every monitor as one image spanning the whole virtual desktop."""
    path = OUT / "all-monitors.png"
    image = capture_screen(path, all_screens=True)
    _show(path, f"All monitors — {image.width}x{image.height}")


def on_this_monitor():
    """Grab only the monitor this window is currently on."""
    monitor = monitor_for_widget(app)
    if monitor is None:
        status.text = "Could not work out which monitor this window is on."
        return
    path = OUT / "this-monitor.png"
    image = capture_monitor(monitor, path)
    _show(path, f"{monitor.name} at ({monitor.x}, {monitor.y}) — "
                f"{image.width}x{image.height}")


def on_delayed():
    """Count down, then grab the screen — time to bring another window up.

    `schedule.every` returns a job; cancelling it stops the repeat.
    """
    remaining = [3]
    status.text = "Capturing in 3 s — switch to another window now."

    def tick():
        remaining[0] -= 1
        if remaining[0] > 0:
            status.text = f"Capturing in {remaining[0]} s…"
            return
        job.cancel()
        path = OUT / "delayed.png"
        image = capture_screen(path, all_screens=True)
        _show(path, f"Delayed capture — {image.width}x{image.height}")

    job = app.schedule.every(1000, tick)


def on_window():
    """Grab this window's content area, trimming the border artifact."""
    path = OUT / "app.png"
    image = capture_widget(app, path, inset=2)
    _show(path, f"This window — {image.width}x{image.height}")


def on_widget():
    """Grab just the button row, to show that any widget works."""
    path = OUT / "body.png"
    image = capture_widget(buttons, path)
    _show(path, f"Button row only — {image.width}x{image.height}")


def _show(path, caption):
    # Reassigning `image` re-reads the file, so repeat captures refresh.
    preview.image = str(path)
    status.text = f"{caption}\n{path}"
    print(caption, "->", path)


with bs.App(title="Screen capture demo", padding=16, gap=12, size=(760, 620)) as app:
    bs.Label("Screen capture", font="heading-lg")
    bs.Label("Each button writes a PNG and previews it below.", font="caption")

    with bs.Row(gap=8) as buttons:
        bs.Button("All monitors", accent="primary", on_click=on_all_monitors)
        bs.Button("This monitor", on_click=on_this_monitor)
        bs.Button("In 3 s", on_click=on_delayed)
        bs.Button("This window", on_click=on_window)
        bs.Button("Button row", on_click=on_widget)

    status = bs.Label("No capture yet.", font="caption")
    # grow=1 claims the leftover vertical space; horizontal="stretch" fills the
    # cross axis. Without the stretch a Picture collapses to its natural width,
    # which for an empty one is a single pixel.
    preview = bs.Picture(
        fit="contain", corner_radius=4, surface="card",
        grow=1, horizontal="stretch",
    )

for _m in list_monitors():
    print(f"monitor {_m.name}: x={_m.x} y={_m.y} {_m.width}x{_m.height} "
          f"primary={_m.is_primary}")
print("output folder:", OUT)
app.run()