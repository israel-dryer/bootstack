"""Probe: the data-cache cleanup at `_patched_bind`'s `widget.after_idle(...)`.

Finding: that deferred cleanup is scheduled on the WIDGET, not on the root, so a
handler that destroys its own widget leaves a pending `after` callback whose
command `destroy()` has already swept. This is the same defect class the
`_patched_unbind` comment documents one screen down.

This code is PRE-EXISTING (unchanged by the #392 branch).

Run: py -3.12 development/probe_392_datacache_afteridle.py
"""

import bootstack as bs


def destroy_from_handler():
    app = bs.App(title="destroy-in-handler")
    root = app.tk.winfo_toplevel()
    root.update()

    with app:
        btn = bs.Button("go")
    root.update()

    errors = []
    root.tk.createcommand('bgerror', lambda msg, *a: errors.append(str(msg)))
    try:
        # The handler destroys the very widget the deferred cleanup is bound to.
        btn.on("click", lambda e: btn.destroy())
        btn.emit("click", data={'payload': 1})
        root.update()
        root.update_idletasks()
        print(f"[destroy-in-handler] bgerrors={errors}")
    finally:
        root.tk.deletecommand('bgerror')
        root.destroy()


if __name__ == '__main__':
    destroy_from_handler()
