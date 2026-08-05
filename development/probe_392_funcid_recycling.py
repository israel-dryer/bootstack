"""Probe: does the deferred `deletecommand` in `_patched_unbind` collide with a
funcid that a LATER bind has already reused?

`tkinter.Misc._register` names its Tcl command `repr(id(bound_method)) +
func.__name__`. Every virtual-event wrapper `_patched_bind` registers is named
`wrapper`, so the whole name hinges on `id()`. If cancelling a subscription
drops the last reference to the old bound method, CPython is free to hand the
same address to the next one — and the deferred deletion would then delete a
command that is live again.

Run: py -3.12 development/probe_392_funcid_recycling.py
"""

import tkinter as tk

import bootstack as bs


def _bgerror_collector(root):
    """Install a background-error collector; returns (errors, uninstall)."""
    errors = []
    root.tk.createcommand('bgerror', lambda msg, *a: errors.append(str(msg)))
    return errors, lambda: root.tk.deletecommand('bgerror')


def census(n=500):
    """How often does bind -> cancel -> bind hand back the SAME funcid?"""
    app = bs.App(title="census")
    root = app.tk.winfo_toplevel()
    widget = app.tk

    same = 0
    prev = None
    for _ in range(n):
        fid = widget.bind('<<Probe>>', lambda e: None, add='+')
        widget.unbind('<<Probe>>', fid)
        if prev is not None and fid == prev:
            same += 1
        prev = fid
    root.update_idletasks()
    print(f"[census] identical consecutive funcids: {same}/{n - 1}")
    app.tk.winfo_toplevel().destroy()


def public_repro():
    """Cancel a subscription, then subscribe again before the next idle point."""
    app = bs.App(title="repro")
    root = app.tk.winfo_toplevel()
    root.update()

    calls = {'a': 0, 'b': 0, 'c': 0}
    with app:
        btn = bs.Button("go")
    root.update()

    errors, uninstall = _bgerror_collector(root)
    try:
        sub_a = btn.on("click", lambda e: calls.__setitem__('a', calls['a'] + 1))
        sub_a.cancel()
        # No update_idletasks here on purpose: the deletion is still pending.
        btn.on("click", lambda e: calls.__setitem__('b', calls['b'] + 1))
        btn.on("click", lambda e: calls.__setitem__('c', calls['c'] + 1))
        root.update_idletasks()  # the pending _delete_command fires here
        btn.emit("click")
        root.update()
        print(f"[repro] calls={calls}  bgerrors={errors}")
    finally:
        uninstall()
        root.destroy()


def cross_widget():
    """Blast radius: does a cancel on widget A kill a later bind on widget B?"""
    app = bs.App(title="cross")
    root = app.tk.winfo_toplevel()
    root.update()

    calls = {'x': 0}
    with app:
        btn_a = bs.Button("a")
        btn_b = bs.Button("b")
    root.update()

    errors, uninstall = _bgerror_collector(root)
    try:
        sub = btn_a.on("click", lambda e: None)
        sub.cancel()
        btn_b.on("click", lambda e: calls.__setitem__('x', calls['x'] + 1))
        root.update_idletasks()
        btn_b.emit("click")
        root.update()
        print(f"[cross] calls={calls}  bgerrors={errors}")
    finally:
        uninstall()
        root.destroy()


def repro_with_idle_gap():
    """Same as public_repro, but let the deferred deletion run BEFORE rebinding.

    If the failure is the pending deletion landing on a recycled funcid, this
    ordering must be clean: the command is already gone when the next bind
    claims the name.
    """
    app = bs.App(title="gap")
    root = app.tk.winfo_toplevel()
    root.update()

    calls = {'a': 0, 'b': 0, 'c': 0}
    with app:
        btn = bs.Button("go")
    root.update()

    errors, uninstall = _bgerror_collector(root)
    try:
        sub_a = btn.on("click", lambda e: calls.__setitem__('a', calls['a'] + 1))
        sub_a.cancel()
        root.update_idletasks()  # <-- the deletion happens HERE, before rebinding
        btn.on("click", lambda e: calls.__setitem__('b', calls['b'] + 1))
        btn.on("click", lambda e: calls.__setitem__('c', calls['c'] + 1))
        btn.emit("click")
        root.update()
        print(f"[idle-gap] calls={calls}  bgerrors={errors}")
    finally:
        uninstall()
        root.destroy()


def control_unique_names():
    """Control experiment: give every registered command a unique name.

    This changes nothing else. If the repro goes green purely because funcids
    stop colliding, the recycled `id()` is the cause, not a coincidence.
    """
    import uuid as _uuid

    def unique_register(self, func, subst=None, needcleanup=1):
        f = tk.CallWrapper(func, subst, self).__call__
        name = 'bs_' + _uuid.uuid4().hex
        self.tk.createcommand(name, f)
        if needcleanup:
            if self._tclCommands is None:
                self._tclCommands = []
            self._tclCommands.append(name)
        return name

    tk.Misc._register = unique_register
    print("[control] unique command names installed")
    public_repro()


if __name__ == '__main__':
    census()
    public_repro()
    cross_widget()
