"""#449 -- can a `<<Change>>` queued with `when="tail"` outlive its widget?

The flake is `test_select_change_event_value_space` seeing `[None, 's']` where it
asserts `['s']`. Instrumenting a full shared-root leg pinned both ends:

    --TEST-- test_select_options_reassignment_reconciles
    EMIT      .!flexframe.!selectbox31.!frame.!textentrypart  'Small' -> None
    --TEST-- test_select_change_event_value_space
    SUBSCRIBE .!flexframe.!selectbox33.!frame.!textentrypart

Two DIFFERENT widgets. Tk path names are never reused (the per-parent counter
only climbs), so the stray `None` cannot be arriving by name. What a queued event
actually carries is the window HANDLE, and `Tk_HandleEvent` dispatches it by
looking that handle up at delivery time -- so a widget created after the emitter
was destroyed can inherit the handle and receive the event.

`tests/conftest.py::_reset_scene` destroys a test's widgets without ever pumping
the event loop, so a `when="tail"` event queued by the last statement of one test
is still in the queue while the next test builds its widgets. That is the window
in which the handle can be reused.

    py -3.12 development/probe_449_queued_event_after_destroy.py [--arm ARM]

Arms:
    control     queue on A and pump WITHOUT destroying A. A must receive its own
                event, or the probe cannot detect delivery at all and a quiet
                `churn` arm would mean nothing.
    churn       the mechanism, with the condition CREATED rather than waited for:
                destroy A with its event still queued, then build B widgets until
                one inherits A's handle. Reports a rate over N rounds.
    drain       the proposed fix -- one `update()` after the emit, before the
                destroy. Same rounds, same churn.

Output is ASCII only (the Windows console is cp1252).
"""
import argparse
import tkinter as tk


def _child(root):
    """A REALIZED child, so it owns a real window handle that can be recycled."""
    w = tk.Frame(root, width=4, height=4)
    w.pack()
    root.update_idletasks()          # force window creation
    return w


def arm_control(root):
    seen = []
    a = _child(root)
    a.bind("<<Change>>", lambda e: seen.append(getattr(e, "data", "<nodata>")))
    a.event_generate("<<Change>>", data="FROM-A", when="tail")
    root.update()
    a.destroy()
    print("  A received its own queued event: %r" % (seen,))
    print("  %s" % ("OK - delivery is detectable" if seen else
                    "BROKEN PROBE - detects nothing; ignore every other arm"))
    return bool(seen)


def _round(root, drain, fanout):
    """One emit/destroy/rebuild cycle. Returns True if a later widget got A's event."""
    a = _child(root)
    a_handle = a.winfo_id()
    a.event_generate("<<Change>>", data="FROM-A", when="tail")

    if drain:
        root.update()                # the proposed fix, applied before the destroy

    a.destroy()

    stray = []
    victims = []
    for _ in range(fanout):
        b = _child(root)
        b.bind("<<Change>>", lambda e, w=b: stray.append((str(w), w.winfo_id())))
        victims.append(b)

    root.update()
    root.update()

    reused = [str(b) for b in victims if b.winfo_id() == a_handle]
    for b in victims:
        b.destroy()
    return bool(stray), bool(reused), a_handle


def arm_churn(root, rounds, fanout, drain=False):
    hits = reuses = 0
    for _ in range(rounds):
        stray, reused, _ = _round(root, drain, fanout)
        hits += bool(stray)
        reuses += bool(reused)
    label = "DRAIN " if drain else "CHURN "
    print("  %s rounds=%d fanout=%d -> handle reused in %d, stray delivery in %d"
          % (label, rounds, fanout, reuses, hits))
    return hits, reuses


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="all", choices=["all", "control", "churn", "drain"])
    ap.add_argument("--rounds", type=int, default=200)
    ap.add_argument("--fanout", type=int, default=6)
    args = ap.parse_args()

    root = tk.Tk()
    root.geometry("240x240+40+40")
    root.update()

    ok = True
    if args.arm in ("all", "control"):
        print("CONTROL -- is delivery detectable at all?")
        ok = arm_control(root)
        print()

    if args.arm in ("all", "churn"):
        print("CHURN -- A destroyed with its event still queued.")
        arm_churn(root, args.rounds, args.fanout, drain=False)
        print()

    if args.arm in ("all", "drain"):
        print("DRAIN -- identical, except the queue is pumped before the destroy.")
        arm_churn(root, args.rounds, args.fanout, drain=True)
        print()

    print("READING: CHURN with a non-zero 'stray delivery' is the mechanism")
    print("reproduced -- an event queued by a destroyed widget reaching a live")
    print("one. DRAIN should read 0 strays for the same rounds; that is the fix")
    print("working. If CONTROL printed BROKEN PROBE, read nothing else here.")
    if not ok:
        print("  ^ CONTROL FAILED, so the quiet arms above are meaningless.")

    root.destroy()


if __name__ == "__main__":
    main()
