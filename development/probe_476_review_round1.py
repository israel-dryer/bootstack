"""Probe for #476 round 1 — measures the double `<<Change>>` on both arms.

Run it twice: once with `optionmenu.py` at `85b051be` (BASELINE) and once at the
branch head (FIXED). It prints which arm it is on by reading the source, so a
run cannot be mislabeled.

    PYTHONPATH=<tree>/src py -3.12 development/probe_476_review_round1.py

Arms:
    emit      one selection through every reachable path, counted
    subs      subscriber counts on the internal's `_textsignal`
    churn     50 `options=` reassignments and 50 `textsignal=` rebinds
    rebind    whether the round 1 test's closing assertion can see the defect
    destroy   the surviving subscription outliving its widget

Everything is ASCII: the Windows box's console is cp1252.
"""
import os
import sys

import bootstack as bs
from bootstack.widgets._impl.primitives.optionmenu import OptionMenu

DECOUPLED = [("One", "1"), ("Two", "2"), ("Three", "3")]


def arm_name() -> str:
    """Read the source to decide which arm this is. Never trust the caller."""
    path = os.path.join(
        os.path.dirname(bs.__file__), "widgets", "_impl", "primitives", "optionmenu.py"
    )
    src = open(path, encoding="utf-8").read()
    return "FIXED" if "self._bind_id = self.textsignal.subscribe" in src else "BASELINE"


def main() -> None:
    print("SRC:", os.path.dirname(bs.__file__))
    print("ARM:", arm_name())

    app = bs.App(title="probe-476")
    app.__enter__()

    # --- emit: the menu path, driven through the real item, not assumed ------
    sb = bs.SelectButton(list(DECOUPLED), value="1", parent=app)
    seen: list = []
    sb.on_change(lambda e: seen.append(e.value))
    app.tk.update()
    items = list(sb._internal._context_menu._impl._items.values())
    items[1].invoke()  # the "Two" radio item
    app.tk.update()
    print(f"menu-click        : {len(seen)}x {seen}  text={sb.text!r} value={sb.value!r}")

    # --- emit: the public signal round trip (#461's path) --------------------
    sig = bs.Signal("1")
    sb2 = bs.SelectButton(list(DECOUPLED), signal=sig, parent=app)
    trace: list = []
    sb2.on_change(lambda e: trace.append(("evt", e.value)))
    app.tk.update()
    trace.clear()
    sb2.value = "2"
    app.tk.update()
    print(f"programmatic set  : sig={sig()!r} trace={trace}")
    trace.clear()
    sig.set("3")
    app.tk.update()
    print(f"signal write      : value={sb2.value!r} text={sb2.text!r} trace={trace}")

    # --- subs: the invariant, across every construction shape ---------------
    sb3 = bs.SelectButton(list(DECOUPLED), value="1", localize=True, parent=app)
    app.tk.update()

    def n(w):
        return len(w._internal._textsignal._subscribers)

    print(f"subscribers       : plain={n(sb)} localized={n(sb3)} signal={n(sb2)}")

    # --- churn: nothing may accumulate --------------------------------------
    m = OptionMenu(app.tk, options=list(DECOUPLED), value="1")
    for i in range(50):
        m.configure(options=[(f"A{i}", str(i)), (f"B{i}", str(i + 100))])
    print(f"50x options=      : {len(m._textsignal._subscribers)}")

    m2 = OptionMenu(app.tk, options=list(DECOUPLED), value="1")
    replaced = []
    for _ in range(50):
        replaced.append(m2._textsignal)
        m2.configure(textsignal=bs.Signal("One"))
    print(
        f"50x textsignal=   : live={len(m2._textsignal._subscribers)} "
        f"orphans_on_replaced={sum(len(s._subscribers) for s in replaced)}"
    )

    # --- rebind: can the round 1 test's closing assertion see the defect? ----
    m3 = OptionMenu(app.tk, options=list(DECOUPLED), value="1")
    previous = m3._textsignal
    m3.configure(textsignal=bs.Signal("Two"))
    print(
        f"one rebind        : on_new={len(m3._textsignal._subscribers)} "
        f"(same on both arms) on_replaced={len(previous._subscribers)} (this is the tell)"
    )

    # --- destroy: pre-existing, recorded as finding 2 ------------------------
    external = bs.Signal("One")
    m4 = OptionMenu(app.tk, options=list(DECOUPLED), textsignal=external)
    app.tk.update()
    live = m4._textsignal
    m4.destroy()
    app.tk.update()
    external.set("Two")  # raises TclError inside the Tk trace, not to us
    app.tk.update()
    print(f"post-destroy      : still_subscribed_on_live_signal={len(live._subscribers)}")
    print("   (a TclError 'bad window path name' is expected above on BOTH arms)")


if __name__ == "__main__":
    sys.exit(main())
