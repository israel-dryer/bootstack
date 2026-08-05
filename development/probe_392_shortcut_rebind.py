"""Probe: does the funcid-recycling window bite a REAL user flow?

Rebinding a shortcut — `unregister(key)` then `register(key, ...)` — unbinds and
rebinds with no idle point in between, which is exactly the window where the
deferred `deletecommand` can land on a funcid the new binding has already
reused. Shortcuts bind REAL events (`<Control-s>`), so this also checks whether
the hazard reaches beyond virtual events.

Run: py -3.12 development/probe_392_shortcut_rebind.py
"""

import bootstack as bs
from bootstack.shortcuts import get_shortcuts


def rebind_shortcut():
    app = bs.App(title="shortcut-rebind")
    root = app.tk.winfo_toplevel()
    with app:
        bs.Label("probe")
    root.update()

    fired = {'old': 0, 'new': 0}
    errors = []
    root.tk.createcommand('bgerror', lambda msg, *a: errors.append(str(msg)))

    sc = get_shortcuts()
    try:
        sc.register("save", "Mod+S", lambda: fired.__setitem__('old', fired['old'] + 1))
        sc.bind_to(root)
        root.update()

        # Rebind the same key to a new command, the way a user would.
        sc.unregister("save")
        sc.register("save", "Mod+S", lambda: fired.__setitem__('new', fired['new'] + 1))

        root.update_idletasks()   # pending deletion lands here
        root.focus_force()
        root.event_generate("<Control-s>")
        root.update()

        print(f"[shortcut-rebind] fired={fired}  bgerrors={errors}")
    finally:
        root.tk.deletecommand('bgerror')
        try:
            sc.unregister("save")
        except KeyError:
            pass
        sc.unbind_from(root)
        root.destroy()


if __name__ == '__main__':
    rebind_shortcut()
