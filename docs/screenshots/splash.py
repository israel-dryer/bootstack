import bootstack as bs

LOGO = "src/bootstack/assets/bootstack.png"


def hero():
    """The splash up on its own — the app reveal is deferred under until='manual'."""
    with bs.App(title=" ", size=(560, 460), padding=0) as app:
        sp = bs.Splash(until="manual", min_duration=0.0, fade=False, size=(500, 420))
        with sp:
            bs.Picture(LOGO, width=180, height=180)
            bs.Label("bootstack", font="heading-lg")
            bs.Label("Loading your workspace…", accent="muted")
            bs.ProgressBar(value=40, mode="indeterminate")

        def place_and_target():
            top = sp._tk_toplevel
            top.geometry("+250+150")  # force onto the primary monitor for capture
            top.attributes("-topmost", True)
            top.lift()
            top.update_idletasks()
            app._capture_target = top

        app.tk.after(850, place_and_target)
    app.run()


SCENES = {"hero": hero}
