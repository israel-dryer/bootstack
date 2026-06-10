"""Hero scene for the Window page — a full OS-window capture of a secondary window.

A `Window` needs a host `App`. The host stays minimal; the runner captures the
`Window` itself (``_capture_target``) as a full OS window (``_capture_full_window``).
"""

import bootstack as bs


def hero():
    _win = [None]
    with bs.App(title=" ", size=(360, 240), padding=0) as app:

        def open_window():
            win = bs.Window(title="Preferences", size=(420, 300), padding=24, gap=14)
            with win:
                bs.Label("Preferences", font="heading-md")
                bs.Switch("Enable notifications", value=True)
                bs.Select(label="Theme", options=["System", "Light", "Dark"], value="System")
                with bs.HStack(gap=8):
                    bs.Button("Save", accent="primary")
                    bs.Button("Cancel", variant="outline")
            win.show()
            _win[0] = win

        def lift_window():
            if not _win[0]:
                return
            top = _win[0]._internal
            top.attributes("-topmost", True)
            top.lift()
            app._capture_full_window = True
            app._capture_target = top

        app.tk.after(200, open_window)
        app.tk.after(850, lift_window)
    app.run()


SCENES = {"hero": hero}
