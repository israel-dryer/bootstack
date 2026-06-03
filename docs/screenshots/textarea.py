import bootstack as bs


def hero():
    with bs.App(title="TextArea", padding=20, minsize=(720, 1)) as app:
        app.tk.maxsize(720, 9999)
        ta = bs.TextArea(
            label="Description",
            placeholder="Write a short description…",
            message="Markdown supported.",
            height=4,
            fill="x",
        )
        app.tk.after(200, ta.focus)
    app.run()


def states():
    with bs.App(title="TextArea — States", padding=20, minsize=(720, 1)) as app:
        app.tk.maxsize(720, 9999)
        with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
            bs.TextArea(value="Editable content.",  label="Normal",    height=3, width=1)
            bs.TextArea(value="Read-only content.", label="Read only", height=3, width=1, read_only=True)
    app.run()


def scrollbars():
    with bs.App(title="TextArea — Scrollbars", padding=20, minsize=(720, 1)) as app:
        app.tk.maxsize(720, 9999)
        with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
            bs.TextArea(label="None",     scrollbars="none",     height=4, width=1,
                        value="Line 1\nLine 2\nLine 3\nLine 4")
            bs.TextArea(label="Vertical", scrollbars="vertical", height=4, width=1,
                        value="Line 1\nLine 2\nLine 3\nLine 4")
            bs.TextArea(label="Both",     scrollbars="both",     height=4, width=1,
                        value="Line 1\nLine 2\nLine 3\nLine 4")
    app.run()


SCENES = {
    "hero":       hero,
    "states":     states,
    "scrollbars": scrollbars,
}