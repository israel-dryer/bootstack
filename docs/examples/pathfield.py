"""PathField — full feature demo.

Demonstrates dialog modes, file filters, label and message text, reactive
signal binding, states, and change event handling.

Run with:
    python docs/examples/pathfield.py
"""

import bootstack as bs

with bs.App(title="PathField Demo", padding=20, gap=16) as app:

    # Basic usage
    bs.Label("Basic", font="heading-sm")
    bs.PathField(placeholder="Select a file…")

    # Dialog modes
    bs.Label("Dialog Modes", font="heading-sm")
    bs.PathField(label="Open file",        mode="open",          placeholder="Select a file…")
    bs.PathField(label="Open multiple",    mode="open_multiple", placeholder="Select files…")
    bs.PathField(label="Save file",        mode="save",          placeholder="Choose save location…")
    bs.PathField(label="Select directory", mode="directory",     placeholder="Select a folder…")

    # File filters
    bs.Label("File Filters", font="heading-sm")
    bs.PathField(
        label="Image file",
        file_filters=[("Images", "*.png *.jpg *.jpeg *.gif"), ("All Files", "*.*")],
        placeholder="Select an image…",
    )

    # Label and message
    bs.Label("Label and Message", font="heading-sm")
    bs.PathField(
        label="Project folder",
        message="Must contain a pyproject.toml or setup.py.",
        placeholder="Select a folder…",
        mode="directory",
        required=True,
    )

    # Reactive binding
    bs.Label("Reactive Binding", font="heading-sm")
    path_sig = bs.Signal("")
    bs.PathField(label="Pick a file", textsignal=path_sig)
    bs.Label(textsignal=path_sig, accent="secondary")

    # States
    bs.Label("States", font="heading-sm")
    bs.PathField(value="/home/user/docs/report.pdf", label="Normal")
    bs.PathField(value="/home/user/docs/report.pdf", label="Read only", read_only=True)
    bs.PathField(value="/home/user/docs/report.pdf", label="Disabled",  disabled=True)

    # Handling changes
    bs.Label("Handling Changes", font="heading-sm")
    last = bs.Signal("(none)")
    pf = bs.PathField(label="Choose a file")
    pf.on_change(lambda e: last.set(pf.value))
    bs.Label(textsignal=last, accent="secondary")

app.run()