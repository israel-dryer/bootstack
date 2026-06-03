import bootstack as bs


def hero():
    with bs.App(title="PathField", padding=20, minsize=(720, 1)) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True, anchor_items="n"):
            pf = bs.PathField(
                label="Source file",
                message="Accepted formats: .py, .txt, .csv",
                placeholder="Select a file…",
            )
            bs.PathField(
                label="Output directory",
                placeholder="Select a folder…",
                mode="directory",
            )
        app.tk.after(200, pf.focus)
    app.run()


def labels():
    with bs.App(title="PathField — Labels", padding=20, minsize=(720, 1)) as app:
        with bs.HStack(gap=12, fill="x", fill_items="x", expand_items=True, anchor_items="n"):
            bs.PathField(
                label="Source file",
                placeholder="Select a file…",
                message="Accepted formats: .py, .txt, .csv",
            )
            bs.PathField(
                label="Output directory",
                placeholder="Choose output folder…",
                mode="directory",
                required=True,
            )
    app.run()


def states():
    with bs.App(title="PathField — States", padding=20, minsize=(720, 1)) as app:
        with bs.HStack(gap=8, fill="x", fill_items="x", expand_items=True):
            bs.PathField(value="/home/user/docs/report.pdf", label="Normal")
            bs.PathField(value="/home/user/docs/report.pdf", label="Read only", read_only=True)
            bs.PathField(value="/home/user/docs/report.pdf", label="Disabled",  disabled=True)
    app.run()


SCENES = {
    "hero":   hero,
    "labels": labels,
    "states": states,
}