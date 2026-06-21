import bootstack as bs


def hero():
    with bs.App(title="Tooltip", size=(240, 130), padding=24) as app:
        btn = bs.Button("Save")
        tip = bs.Tooltip(btn, "Save your changes to disk.",
                         anchor_point="s", window_point="n")

        def trigger():
            btn.tk.event_generate('<Enter>')

        def ensure_topmost():
            if tip._internal._toplevel:
                tip._internal._toplevel.attributes('-topmost', True)

        app.tk.after(600, trigger)
        app.tk.after(900, ensure_topmost)
    app.run()


def accents():
    with bs.App(title="Tooltip — Accents", size=(520, 130), padding=24) as app:
        with bs.Row(gap=8, horizontal="stretch"):
            btn_p = bs.Button("Primary")
            bs.Tooltip(btn_p, "Primary tooltip", accent="primary",
                       anchor_point="s", window_point="n")
            btn_s = bs.Button("Success")
            bs.Tooltip(btn_s, "Success tooltip", accent="success",
                       anchor_point="s", window_point="n")
            btn_w = bs.Button("Warning")
            bs.Tooltip(btn_w, "Warning tooltip", accent="warning",
                       anchor_point="s", window_point="n")
            btn_d = bs.Button("Danger")
            tip_d = bs.Tooltip(btn_d, "Danger tooltip", accent="danger",
                               anchor_point="s", window_point="n")

        def trigger():
            btn_d.tk.event_generate('<Enter>')

        def ensure_topmost():
            if tip_d._internal._toplevel:
                tip_d._internal._toplevel.attributes('-topmost', True)

        app.tk.after(600, trigger)
        app.tk.after(900, ensure_topmost)
    app.run()


def anchor():
    # One button with tooltips pinned on three sides, all forced on screen at
    # once for the screenshot. auto_flip=False keeps each one exactly where it
    # is anchored; the button is centered so every tip lands in the window.
    with bs.App(title="Tooltip — Anchors", size=(540, 230), padding=24,
                vertical_items="center") as app:
        btn = bs.Button("More info", accent="primary")
        tips = [
            bs.Tooltip(btn, "Anchored above", auto_flip=False,
                       anchor_point="n", window_point="s"),
            bs.Tooltip(btn, "Anchored below", auto_flip=False,
                       anchor_point="s", window_point="n"),
            bs.Tooltip(btn, "Anchored to the right", auto_flip=False,
                       anchor_point="e", window_point="w"),
        ]

        def trigger():
            for t in tips:
                t._internal._show_tip()

        def ensure_topmost():
            for t in tips:
                if t._internal._toplevel:
                    t._internal._toplevel.attributes('-topmost', True)

        app.tk.after(600, trigger)
        app.tk.after(900, ensure_topmost)
    app.run()


SCENES = {
    "hero":    hero,
    "accents": accents,
    "anchor":  anchor,
}