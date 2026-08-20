"""#458 -- a `Select` bound to a `Signal` shows the option VALUE, not its TEXT.

The report (bLynnb2762, 0.3.2, Windows 11): with decoupled options
`[('One', '1'), ('Two', '2'), ('Three', '3')]`,

    bs.Select(options=..., value='2')            shows "Two"    <- correct
    bs.Select(options=..., signal=bs.Signal('2'))shows "2"      <- reported bug

Four arms. Arms 3 and 4 are what make arms 1 and 2 mean anything:

    ARM 1  value=      -- the working path, the reporter's baseline
    ARM 2  signal=     -- the reported path
    ARM 3  CONTROL, plain options (text == value) through BOTH paths. If the
           defect were "signal does not seed the entry at all", this arm would
           break too. It must stay identical across both paths, which scopes
           the defect to the text<->value DECOUPLING rather than to seeding.
    ARM 4  the signal written AFTER construction, not seeded at it -- separates
           "the constructor skips the mapping" from "the binding never maps".

Each arm reports what the ENTRY DISPLAYS (what the user sees, which is the
whole report) alongside `.value` / `.selection`, because the reporter noted the
event data looked right -- so display and value must be read separately or the
bug reads as absent.

Run:  py -3.12 development/probe_458_select_signal_display.py
ASCII output only (cp1252 consoles -- see CLAUDE.md).
"""
from __future__ import annotations

import bootstack as bs

DECOUPLED = [("One", "1"), ("Two", "2"), ("Three", "3")]
PLAIN = ["One", "Two", "Three"]


def _read(sel) -> str:
    """What the user SEES, beside what the program reads."""
    shown = sel._internal.entry_widget.get()
    sel_rec = sel.selection
    sel_text = sel_rec.get("text") if isinstance(sel_rec, dict) else sel_rec
    return f"shows={shown!r:8} .value={sel.value!r:6} .selection.text={sel_text!r}"


def main() -> None:
    with bs.App(title="probe 458") as app:
        print("ARM 1 -- value='2', decoupled options (the working baseline)")
        a1 = bs.Select(options=list(DECOUPLED), value="2")
        print(f"  {_read(a1)}")

        print("\nARM 2 -- signal=Signal('2'), decoupled options (the REPORT)")
        sig = bs.Signal("2")
        a2 = bs.Select(options=list(DECOUPLED), signal=sig)
        print(f"  {_read(a2)}  signal={sig()!r}")

        print("\nARM 3 -- CONTROL, plain options (text == value), both paths")
        c1 = bs.Select(options=list(PLAIN), value="Two")
        print(f"  value=  {_read(c1)}")
        c2 = bs.Select(options=list(PLAIN), signal=bs.Signal("Two"))
        print(f"  signal= {_read(c2)}")

        print("\nARM 4 -- signal written AFTER construction, decoupled options")
        sig4 = bs.Signal("1")
        a4 = bs.Select(options=list(DECOUPLED), signal=sig4)
        print(f"  seeded '1':      {_read(a4)}")
        sig4.set("3")
        app.tk.update_idletasks()
        print(f"  after set('3'):  {_read(a4)}  signal={sig4()!r}")

        print("\nREADING -- stated as a comparison, not as a verdict, so this")
        print("text does not go stale the moment the defect is fixed.")
        print("  arm 1 vs arm 2:  DIFFER  -> defect present (signal path skips")
        print("                              the value->text map)")
        print("                   AGREE   -> fixed")
        print("  arm 3 (control): must be identical in BOTH states. If it ever")
        print("                   moves, the change reached plain options, which")
        print("                   it must not -- there text == value.")
        print("  arm 4:           tracks whether the signal drives the field on")
        print("                   every write, or only seeds it at construction.")


if __name__ == "__main__":
    main()
