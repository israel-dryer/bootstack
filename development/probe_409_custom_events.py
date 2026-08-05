"""Probe for #409 — what the custom-event surface actually does.

Run: py -3.12 development/probe_409_custom_events.py   (exit 0 = all as recorded)

WHY THIS EXISTS
    docs/reference/events.rst claimed "any name that isn't a built-in event is
    treated as a custom event" and showed on("row_imported") / emit("row_imported").
    Both raise. But the first read of that was too broad -- it is NOT that custom
    events are unbuilt. The mechanism works two ways (C and D below); what is
    missing is only the BARE-NAME-ON-A-STOCK-WIDGET spelling, because
    resolve_event() has no fallback branch for an unregistered plain name.

    That distinction is the whole decision: building the fallback is ~1 line
    (`return f"<<{name}>>"`), but it is the same line that makes B raise today.

Checks A/B are the cost side, C/D are the capability side, E guards the example
that survived in the rewritten docs section.
"""
from __future__ import annotations

import bootstack as bs
from bootstack.errors import UnknownEventError
from bootstack.events import ChangeEvent

# Internal on purpose: this probe records that the bare-name path exists but is
# NOT public API. Promoting it is the open question left on #409.
from bootstack.widgets._core.events import register_widget_events

failures: list[str] = []


def check(label: str, got, want) -> None:
    ok = got == want
    print(f"[{'PASS' if ok else 'FAIL'}] {label}\n       got={got!r}")
    if not ok:
        failures.append(f"{label}: got {got!r}, want {want!r}")


def raises_unknown(fn) -> bool:
    try:
        fn()
    except UnknownEventError:
        return True
    except Exception as exc:  # any other error is a different defect
        print(f"       !! unexpected {type(exc).__name__}: {exc}")
        return False
    return False


class Importer(bs.Column):
    """A composite that publishes its own event under a bare name."""


register_widget_events(Importer, {"row_imported": "<<RowImported>>"})

with bs.App(title="probe-409") as app:
    plain = bs.Column()
    field = bs.TextField()
    imp = Importer()

# --- A. the defect #409 reported: bare name, no registration ------------------
check("A1 on('row_imported') on a stock widget raises UnknownEventError",
      raises_unknown(lambda: plain.on("row_imported", lambda e: None)), True)
check("A2 emit('row_imported') on a stock widget raises UnknownEventError",
      raises_unknown(lambda: plain.emit("row_imported", data={"row": 1})), True)

# --- B. CONTROL: the guard a bare-name fallback would cost ---------------------
# Without this, A looks like a pure bug. B is what makes it a tradeoff: the same
# missing branch is what turns a misspelled built-in into a loud error today.
check("B  on('chnage') raises today -- typo guard a fallback would remove",
      raises_unknown(lambda: field.on("chnage", lambda e: None)), True)

# --- C. capability path 1: literal virtual sequence, any stock widget ---------
seen_c: list = []
plain.on("<<RowImported>>", lambda e: seen_c.append(e))
plain.emit("<<RowImported>>", data={"row": 42, "source": "clipboard"})

# --- D. capability path 2: bare name on a class that registered it ------------
seen_d: list = []
imp.on("row_imported", lambda e: seen_d.append(e))
imp.emit("row_imported", data={"row": 7, "source": "file"})

# --- E. the example kept in the rewritten docs section ------------------------
seen_e: list = []
field.on_change(lambda e: seen_e.append(e.value))
field.emit("change", data=ChangeEvent(value="hello"))

app.tk.update()  # virtual events dispatch on the next loop turn

check("C  literal '<<RowImported>>' delivers its payload on a stock widget",
      seen_c, [{"row": 42, "source": "clipboard"}])
check("D  bare 'row_imported' delivers its payload after register_widget_events",
      seen_d, [{"row": 7, "source": "file"}])
check("E  docs example: emit('change', ChangeEvent(...)) reaches on_change",
      seen_e, ["hello"])

print()
if failures:
    print(f"{len(failures)} CHECK(S) DIVERGED from what #409 recorded:")
    for f in failures:
        print(f"  - {f}")
    raise SystemExit(1)
print("All 7 checks match the behavior recorded on #409.")