"""Is the keypad Enter key reachable at all, and does a Text widget answer it?

`Dialog` binds `press_default` to BOTH `<Return>` and `<KP_Enter>` on its
toplevel, and `_key_was_consumed` decides whether to stand down from the
WIDGET the key reached, not from the key itself. That is only sound while the
two Enter keys are equivalent to that widget -- and Tk binds
`Text <KP_Enter>` to the literal script `# nothing` (tk8.6/text.tcl:308,
unconditional), so they are not equivalent wherever the keypad key arrives as
its own keysym.

This probe answers, per platform, whether that case can arise here at all.

Arm 1 (AUTOMATIC, runs anywhere with a display) -- can `event_generate`
synthesize the key? If not, no automated test on this box can cover the
`<KP_Enter>` half of the dialog binding, whatever the physical key does.

Arm 2 (MANUAL, needs a human and a keyboard with a numeric keypad) -- what
does the PHYSICAL key report, and does a `Text` insert a newline for it?
Alternate keypad Enter with the main Enter key: the main key is the control,
and interleaving the two is what rules out reading the same key twice.

MEASURED SO FAR
  Windows 11, Tk 8.6, 2026-08-11: arm 1 FAILS (keysym '??', keycode 0) and
  arm 2 shows the physical keypad key arriving as keysym 'Return', keycode 13,
  char '\\r' -- byte-identical to the main Enter key across four alternating
  presses, with only the `<Return>` toplevel binding firing. Windows FOLDS the
  two keys, so the `<KP_Enter>` binding is unreachable and the Text/`# nothing`
  asymmetry cannot arise.

  X11 and Aqua: UNRUN. X11 is the case that matters -- if the key arrives as
  `KP_Enter` there, a dialog TextArea inserts nothing and `_key_was_consumed`
  stands the dialog down anyway, leaving the key dead.

Run:  py -3.13 development/probe_441_kp_enter_platform.py
Output is ASCII only -- this box's console is cp1252.
"""

from __future__ import annotations

import sys
import tkinter as tk

# ---------------------------------------------------------------------------
# Arm 1 -- automatic: can the key be synthesized?
# ---------------------------------------------------------------------------


def arm1_synthesis() -> None:
    print("ARM 1 -- can event_generate synthesize <KP_Enter>?")
    root = tk.Tk()
    root.geometry("300x200+100+100")
    root.deiconify()
    text = tk.Text(root, height=4)
    text.pack(fill="both", expand=True)
    root.update()
    text.focus_force()
    root.update()

    if not text.winfo_ismapped():
        print("  SKIP: widget is not mapped, synthesized keys would be dropped")
        root.destroy()
        return

    seen: list[tuple[str, int, str]] = []
    text.bind("<Key>", lambda e: seen.append((e.keysym, e.keycode, e.char)), add="+")

    for key in ("<Return>", "<KP_Enter>"):
        before = text.get("1.0", "end-1c")
        mark = len(seen)
        text.event_generate(key)
        root.update()
        delivered = seen[mark:]
        gained = text.get("1.0", "end-1c") != before
        if not delivered:
            print(f"  {key:<12} -> NOTHING DELIVERED")
        else:
            keysym, keycode, char = delivered[0]
            print(
                f"  {key:<12} -> keysym={keysym!r} keycode={keycode} "
                f"char={char!r} inserted={gained}"
            )
            if keysym == "??":
                print(
                    "                  ^ dead event: this window system cannot "
                    "map the keysym\n"
                    "                    back to a keycode, so synthesis "
                    "cannot reach this path."
                )
        text.delete("1.0", "end")

    print(
        "  class binding: Text <KP_Enter> = "
        f"{str(root.bind_class('Text', '<KP_Enter>'))!r}"
    )
    root.destroy()
    print()


# ---------------------------------------------------------------------------
# Arm 2 -- manual: what does the physical key report?
# ---------------------------------------------------------------------------


def arm2_physical() -> None:
    print("ARM 2 -- press the PHYSICAL keys (needs a numeric keypad)")
    print("  Alternate: KEYPAD Enter, MAIN Enter, KEYPAD Enter, MAIN Enter.")
    print("  Close the window when done.\n")

    root = tk.Tk()
    root.title("press KEYPAD Enter and MAIN Enter, alternating")
    root.geometry("760x420+200+120")

    tk.Label(
        root,
        text="Click the box, then alternate KEYPAD Enter and MAIN Enter.",
        font=("Segoe UI", 10, "bold"),
    ).pack(anchor="w", padx=8, pady=(8, 0))

    text = tk.Text(root, height=5)
    text.pack(fill="x", padx=8, pady=8)

    log = tk.Listbox(root, height=12, font=("Consolas", 9))
    log.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def note(msg: str) -> None:
        log.insert("end", msg)
        log.see("end")
        print(msg)

    # Mirror the dialog: bind press_default's two keys on the toplevel and
    # report which one actually fires.
    for key in ("<Return>", "<KP_Enter>"):
        root.bind(key, lambda e, k=key: note(f"  toplevel binding {k} FIRED"))

    def on_key(event: tk.Event) -> None:
        if event.keysym not in ("Return", "KP_Enter"):
            return
        before = text.get("1.0", "end-1c")
        keysym, keycode, char = event.keysym, event.keycode, event.char

        def after() -> None:
            gained = text.get("1.0", "end-1c") != before
            note(
                f"    keysym={keysym!r} keycode={keycode} char={char!r} "
                f"-> Text inserted newline: {gained}"
            )

        text.after_idle(after)

    text.bind("<Key>", on_key, add="+")

    note("Ready. Identical readings for both keys means this platform FOLDS")
    note("them, and the <KP_Enter> binding is unreachable here.")
    note("")

    text.focus_force()
    root.mainloop()


if __name__ == "__main__":
    print(f"platform: {sys.platform}")
    root = tk.Tk()
    root.withdraw()
    print(f"windowingsystem: {root.tk.call('tk', 'windowingsystem')}")
    print(f"Tk: {root.tk.call('info', 'patchlevel')}\n")
    root.destroy()

    arm1_synthesis()

    if "--auto" in sys.argv:
        print("ARM 2 -- SKIPPED (--auto): needs a human keypress.")
    else:
        arm2_physical()
