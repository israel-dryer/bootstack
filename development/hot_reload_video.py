"""Video-staging demo for hot reload.

Record:  bootstack dev development/hot_reload_video.py

Put your editor and this window side by side, then follow the shot list at the
bottom of this file. The counter is module-level, so it survives every reload —
that's the beat to feature.
"""
import bootstack as bs

clicks = bs.Signal(0)  # module-level -> survives reloads (the "wow" moment)

with bs.App(title="bootstack — hot reload", size=(460, 420), padding=28, gap=20) as app:
    with app.add_toolbar() as tb:
        tb.add_label("Hot Reload Demo", font="heading-md")
        tb.add_spacer()
        tb.add_theme_toggle()

    bs.Label("Edit this file and save.", font="heading-lg")
    bs.Label("The window updates in place — no restart.", accent="muted")

    with bs.Card(padding=20, gap=12):
        bs.Label("Live state", font="heading-md")
        bs.Label(textsignal=clicks.map(lambda n: f"You clicked {n} times."))
        bs.Button("Click me", accent="primary",
                  on_click=lambda: clicks.set(clicks() + 1))

app.run()


# --- Shot list (delete before recording, or keep — it's just a comment) -------
#
# 1. Launch with `bootstack dev`. Editor left, app right.
# 2. Change "Edit this file and save." -> a new headline. Save. (instant text)
# 3. Change the Button accent="primary" -> accent="success". Save. (recolor)
# 4. Add a line below the button:  bs.Label("Added live!", accent="info")
#    Save. (a widget appears)
# 5. THE BEAT: click the button 5 times. Now edit ANY label text and save.
#    The count stays at 5 — state survived the reload.
# 6. Break it: delete the closing quote on a label. Save.
#    -> red error banner in the window; the app stays alive. Fix it, save -> recovers.
# 7. (optional) Click the theme toggle to show light/dark.
