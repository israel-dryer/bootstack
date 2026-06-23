"""Splash — a borderless intro screen shown while the app builds.

Run this directly: the splash appears first, covers the (simulated) cost of
building the main window, and dismisses after its timer — revealing the app.
"""

import bootstack as bs
from bootstack.images import get_icon

with bs.App(title="Splash", size=(620, 420), padding=16, gap=12) as app:
    # Written first, so it covers everything that follows. The timer closes it
    # after 2.5s; min_duration keeps it up at least 1s on a fast machine.
    with bs.Splash(until=2.5, min_duration=1.0, skippable=True, size=(420, 360)):
        bs.Picture(get_icon("rocket", size=96, color="primary"), width=96, height=96)
        bs.Label("My App", font="heading-lg")
        bs.Label("Loading your workspace…", accent="muted")
        # Timed mode keeps the splash up under the live event loop, so an
        # indeterminate bar actually marches. (Under until="ready", covering a
        # synchronous build, it would sit still — see the splash how-to.)
        bar = bs.ProgressBar(mode="indeterminate")
        bar.start()

    # The heavy app body — the splash is on screen the whole time it builds.
    bs.Label("Welcome!", font="heading-md")
    bs.Label("The splash covered the cost of building this window.")

app.run()