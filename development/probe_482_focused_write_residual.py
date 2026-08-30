"""#482 -- is the focused-write residual real, reachable, and worth filing?

The fix commits a programmatic write only when the field does NOT hold keyboard
focus. A write made while it DOES is indistinguishable from typing at that seam
and still lags. Four questions decide whether that needs an issue:

  is it real      A/B  -- the same write unfocused, then focused
  is it NEW       C    -- the other programmatic path, `.value =`, side by side
                          (and run the whole file against main: B must match)
  does it heal    D    -- blur after B
  is it REACHABLE F/G  -- a button press, the usual trigger for such a write
                  H    -- a timer, with no pointer involved
                  I/J  -- a keyboard shortcut, which fires without moving focus

Arm A is the control: the same write UNFOCUSED must follow, or the probe is not
reaching the fixed path and every other arm is noise.

Run once per arm and diff:

    py -3.12 development/probe_482_focused_write_residual.py
    PYTHONPATH=<main-worktree>/src py -3.12 <abs>/development/probe_482_focused_write_residual.py

PRECONDITION, and it has bitten once: `focus_get()` is the fix's own
discriminator and reports None whenever the toplevel is not active, which reads
as "unfocused" and makes the residual look fixed. Asserting focus BEFORE an
`after()` is not enough either -- Tk focus falls back to the toplevel during the
mainloop transition, so the write lands unfocused and reports FOLLOWS for the
wrong reason. Every arm below records the discriminator AT the moment of the
write and reports INCONCLUSIVE rather than a verdict when it disagrees.
"""
import os

import bootstack as bs
from bootstack.shortcuts import get_shortcuts

print("PROVENANCE", os.path.dirname(bs.__file__))

app = bs.App(title="probe482res")
root = app.tk.winfo_toplevel()
root.geometry("420x320+60+60")
root.deiconify()
root.update()
root.focus_force()
root.update()


def arm(label, fn):
    try:
        print("[%s] %s" % (label, fn()))
    except Exception as exc:
        print("[%s] EXC %s: %s" % (label, type(exc).__name__, exc))


def entry_of(field):
    return field._internal._entry


def verdict(field, expected):
    got = field.value
    return "value=%r %s" % (got, "FOLLOWS" if got == expected else "LAGS")


def make(cls, sig):
    f = cls(parent=app, textsignal=sig)
    root.update()
    return f


def field_with_focus(cls=bs.TextField):
    sig = bs.Signal("start")
    f = make(cls, sig)
    e = entry_of(f)
    e.focus_force()
    root.update()
    return sig, f, e


# ---- A: control. Unfocused write must follow, or nothing below means anything.
def a_control_unfocused(cls=bs.TextField):
    sig = bs.Signal("start")
    f = make(cls, sig)
    root.focus_force()
    root.update()
    sig.set("by code")
    root.update()
    return verdict(f, "by code")


# ---- B: the residual. Focused write.
def b_focused_signal_write(cls=bs.TextField):
    sig, f, e = field_with_focus(cls)
    if e.focus_get() is not e:
        return "INCONCLUSIVE -- entry never took focus (window not active?)"
    sig.set("by code")
    root.update()
    return verdict(f, "by code")


# ---- C: discriminator. The OTHER programmatic path, same focused condition.
def c_focused_value_setter(cls=bs.TextField):
    sig, f, e = field_with_focus(cls)
    if e.focus_get() is not e:
        return "INCONCLUSIVE -- entry never took focus (window not active?)"
    f.value = "by code"
    root.update()
    return verdict(f, "by code")


# ---- D: does B heal, or is it permanent like the round-1 defect was?
def d_heals_on_blur():
    sig, f, e = field_with_focus()
    if e.focus_get() is not e:
        return "INCONCLUSIVE -- entry never took focus (window not active?)"
    sig.set("by code")
    root.update()
    before = f.value
    root.focus_force()          # blur the entry
    root.update()
    return "before_blur=%r  after_blur=%r  %s" % (
        before, f.value, "HEALS" if f.value == "by code" else "PERMANENT")


# ---- E: does the user SEE the new text while value disagrees?
def e_display_vs_value():
    sig, f, e = field_with_focus()
    if e.focus_get() is not e:
        return "INCONCLUSIVE -- entry never took focus (window not active?)"
    sig.set("by code")
    root.update()
    return "display=%r value=%r sig=%r" % (e.get(), f.value, sig())


# ---- F/G: a button, the usual trigger. Does pressing one blur the field first?
def press(widget):
    w = widget.tk if hasattr(widget, "tk") else widget
    w.event_generate("<ButtonPress-1>", x=5, y=5)
    w.event_generate("<ButtonRelease-1>", x=5, y=5)
    root.update()


def f_button_press_blurs():
    sig, f, e = field_with_focus()
    b = bs.Button("Go", parent=app, on_click=lambda: None)
    root.update()
    e.focus_force()
    root.update()
    if e.focus_get() is not e:
        return "INCONCLUSIVE -- entry never took focus"
    press(b)
    still = e.focus_get() is e
    return "entry still focused after press: %s -> %s" % (
        still,
        "residual REACHED by a button" if still
        else "button BLURS, the write lands on the fixed path")


def g_end_to_end_button():
    sig, f, e = field_with_focus()
    b = bs.Button("Fill", parent=app, on_click=lambda: sig.set("by code"))
    root.update()
    e.focus_force()
    root.update()
    if e.focus_get() is not e:
        return "INCONCLUSIVE -- entry never took focus"
    press(b)
    return "display=%r %s" % (e.get(), verdict(f, "by code"))


# ---- H: a timer write, no pointer involved.
def h_scheduled_write():
    sig, f, e = field_with_focus()
    note = {}

    def do_write():
        note["focus"] = root.tk.call("focus")
        note["is_entry"] = e.focus_get() is e
        sig.set("by code")

    root.after(10, lambda: e.focus_force())
    root.after(40, do_write)
    root.after(100, root.quit)
    root.mainloop()
    if not note.get("is_entry"):
        return "INCONCLUSIVE -- focus was %s at the write" % note.get("focus")
    return "focused at write=True  display=%r %s" % (e.get(), verdict(f, "by code"))


# ---- I/J: a keyboard shortcut. It fires without the pointer, so nothing moves
# focus off the field the user is typing in -- "Mod+R resets this form".
def i_shortcut_keeps_focus():
    sig, f, e = field_with_focus()
    if e.focus_get() is not e:
        return "INCONCLUSIVE -- entry never took focus"
    note = {}
    sc = get_shortcuts()
    sc.register("probe.reset.i", "Mod+R",
                lambda: note.update(is_entry=(e.focus_get() is e)))
    sc.bind_to(root)
    try:
        e.event_generate("<Control-r>")
        root.update()
    finally:
        sc.unregister("probe.reset.i")
    if "is_entry" not in note:
        return "INCONCLUSIVE -- shortcut handler never ran"
    return "handler ran with entry focused: %s" % note["is_entry"]


def j_shortcut_writes_signal():
    sig, f, e = field_with_focus()
    if e.focus_get() is not e:
        return "INCONCLUSIVE -- entry never took focus"
    note = {}

    def reset():
        note["is_entry"] = e.focus_get() is e
        sig.set("by code")

    sc = get_shortcuts()
    sc.register("probe.reset.j", "Mod+R", reset)
    sc.bind_to(root)
    try:
        e.event_generate("<Control-r>")
        root.update()
    finally:
        sc.unregister("probe.reset.j")
    if not note.get("is_entry"):
        return "INCONCLUSIVE -- entry not focused when the handler wrote"
    return "display=%r %s" % (e.get(), verdict(f, "by code"))


arm("A  control unfocused   TextField    ", a_control_unfocused)
arm("A  control unfocused   SpinnerField ", lambda: a_control_unfocused(bs.SpinnerField))
arm("B  focused sig.set     TextField    ", b_focused_signal_write)
arm("B  focused sig.set     SpinnerField ", lambda: b_focused_signal_write(bs.SpinnerField))
arm("B  focused sig.set     PasswordField", lambda: b_focused_signal_write(bs.PasswordField))
arm("C  focused .value=     TextField    ", c_focused_value_setter)
arm("C  focused .value=     SpinnerField ", lambda: c_focused_value_setter(bs.SpinnerField))
arm("D  heal on blur                     ", d_heals_on_blur)
arm("E  display vs value                 ", e_display_vs_value)
arm("F  does a button blur?              ", f_button_press_blurs)
arm("G  end to end via button            ", g_end_to_end_button)
arm("H  timer write                      ", h_scheduled_write)
arm("I  shortcut keeps focus?            ", i_shortcut_keeps_focus)
arm("J  end to end via shortcut          ", j_shortcut_writes_signal)

root.destroy()
