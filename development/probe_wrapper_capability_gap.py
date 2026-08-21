"""Mode 6 -- CAPABILITY GAP: what can the internal do that the wrapper cannot reach?

WHY THIS EXISTS
---------------
The #463 wrapper audit measured five modes and all five take a CONSTRUCTOR
KEYWORD as their unit:

    1 never forwarded   2 wrong destination   3 swallowed as a layout key
    4 accepted then ignored                   5 the type lies

A missing PROPERTY or METHOD is invisible to every one of them. #465 is the
proof: `Select` forwards every parameter it declares -- clean under modes 1-5 --
while exposing no way to read a validation outcome its internal has fully wired.
An external user found by hand, three days later, what the audit was built to
find mechanically.

So this arm asks a different question: for each public wrapper, what does
`self._internal` expose that the wrapper does not?

WHAT THIS IS NOT
----------------
It is NOT a defect list. It is a CANDIDATE list that needs classifying, and the
audit already paid to learn why: mode 2 flagged 100 rows to find 1 real defect,
and three of that pass's five tool defects were FALSE ALARMS pointing at working
code. Most rows here will be deliberate -- a wrapper exists precisely to NOT
expose the toolkit. Read `--arm control` before believing any row.

Every wrapper is CONSTRUCTED, not read. The audit's own habit: a static wrapper
scan that is not cross-checked against construction ships false findings.

ARMS
  --arm scan      the gap table (default)
  --arm control   proves the scan can find something -- it must report #465's
                  own two members, and must NOT report a member the wrapper has
"""
from __future__ import annotations

import argparse
import sys

# Members every Tk/ttk widget carries. Subtracting these is what separates
# "the internal has a bootstack capability the wrapper hides" from "the internal
# is a Tk widget and the wrapper is deliberately not one" -- which is the entire
# design of this framework, not a finding.
def _toolkit_baseline() -> set[str]:
    import tkinter
    from tkinter import ttk
    base: set[str] = set()
    for cls in (tkinter.Misc, tkinter.Pack, tkinter.Grid, tkinter.Place,
                tkinter.Widget, tkinter.Wm, ttk.Widget, ttk.Frame,
                tkinter.Entry, tkinter.Text, tkinter.Canvas, tkinter.Menu):
        base |= {n for n in dir(cls) if not n.startswith("_")}
    return base


def _public(obj) -> set[str]:
    return {n for n in dir(obj) if not n.startswith("_")}


def _classify(name: str) -> str:
    """Rank a gap row. Reuses the audit's lesson: DIVERGENCE is what ranks, not
    the raw delta -- a member the SIBLING wrappers expose is a far stronger
    candidate than one nobody exposes."""
    if name in _SIBLING_SURFACE:
        return "SIBLINGS-HAVE-IT"
    return "internal-only"


_SIBLING_SURFACE: set[str] = set()


def _collect(bs) -> tuple[list, list[str]]:
    """Construct every exported widget bare and diff wrapper vs internal."""
    global _SIBLING_SURFACE
    baseline = _toolkit_baseline()
    rows, skipped = [], []

    names = [n for n in getattr(bs, "__all__", []) if n[:1].isupper()]
    app = bs.App(title="probe-mode6")
    built = {}
    with app:
        for cname in sorted(names):
            cls = getattr(bs, cname, None)
            if not isinstance(cls, type):
                continue
            try:
                w = cls()
            except Exception as exc:                # noqa: BLE001 -- reported
                skipped.append("%-18s could not build bare (%s)"
                               % (cname, type(exc).__name__))
                continue
            internal = getattr(w, "_internal", None)
            if internal is None:
                skipped.append("%-18s no _internal" % cname)
                continue
            built[cname] = (w, internal)

        # The sibling surface: everything ANY wrapper chose to expose. A member
        # sitting on an internal while its siblings' wrappers publish it is the
        # #465 shape exactly.
        for w, _ in built.values():
            _SIBLING_SURFACE |= _public(w)

        for cname, (w, internal) in built.items():
            gap = _public(internal) - _public(w) - baseline
            for member in sorted(gap):
                rows.append((cname, member, _classify(member),
                             type(internal).__name__))
    return rows, skipped


def scan() -> int:
    import bootstack as bs
    rows, skipped = _collect(bs)

    strong = [r for r in rows if r[2] == "SIBLINGS-HAVE-IT"]
    weak = [r for r in rows if r[2] != "SIBLINGS-HAVE-IT"]

    print("MODE 6 -- CAPABILITY GAP")
    print("=" * 72)
    print("wrappers analysed : %d" % len({r[0] for r in rows}))
    print("gap rows          : %d  (%d strong / %d weak)"
          % (len(rows), len(strong), len(weak)))
    print()
    print("STRONG -- the internal exposes it AND some sibling wrapper publishes")
    print("it, so hiding it here is a divergence, not a design choice.")
    print("-" * 72)
    by_cls: dict[str, list[str]] = {}
    for cname, member, _, _i in strong:
        by_cls.setdefault(cname, []).append(member)
    for cname in sorted(by_cls):
        print("  %-16s %s" % (cname, ", ".join(sorted(by_cls[cname]))))
    if not by_cls:
        print("  (none)")
    print()
    print("WEAK -- internal-only; most are deliberate. Not a defect list.")
    print("-" * 72)
    weak_by: dict[str, int] = {}
    for cname, _m, _c, _i in weak:
        weak_by[cname] = weak_by.get(cname, 0) + 1
    for cname in sorted(weak_by, key=lambda c: -weak_by[c])[:12]:
        print("  %-16s %d members" % (cname, weak_by[cname]))
    print()
    if skipped:
        print("NOT ANALYSED (%d) -- a hole in the coverage, not coverage:" % len(skipped))
        for s in skipped:
            print("  " + s)
    return 0


def control() -> int:
    """The scan must be shown able to find something before a quiet row means
    anything. #465 is the known-positive: Select's internal reaches validation
    signals its wrapper does not publish."""
    import bootstack as bs
    rows, _ = _collect(bs)
    sel = {m for c, m, _k, _i in rows if c == "Select"}

    print("CONTROL")
    print("=" * 72)
    ok = True

    # Arm 1 -- known positive. Asserts ONLY on the scan's own output.
    #
    # The first version of this arm read `member in sel or not hasattr(...)`.
    # The second clause is true whenever the member is missing, so the arm
    # passed without testing the scan at all -- a control written to pass,
    # which is the exact defect this file exists to guard against. Assert on
    # `sel` and nothing else.
    for member in ("on_valid", "insert_addon"):
        hit = member in sel
        print("  arm1 scan reports Select gap %-12s -> %s"
              % (member, "YES" if hit else "NO (BAD)"))
        if not hit:
            ok = False
            print("       ^ the scan found nothing it is known to find.")

    # Arm 2 -- known negative. A member the wrapper DOES publish must not be
    # reported as a gap, or the scan is a false-alarm generator.
    for member in ("value", "options"):
        bad = member in sel
        print("  arm2 Select gap wrongly lists %-8s -> %s"
              % (member, "YES (BAD)" if bad else "no"))
        if bad:
            ok = False

    # Arm 3 -- THE KNOWN LIMIT, asserted so it cannot be mistaken for coverage.
    #
    # This probe was written FOR #465 and it CANNOT SEE #465. The capability
    # sits two hops down (`_internal._entry._valid_signal`) behind underscore
    # names, while this scan diffs one hop (`_internal`) over public names only.
    # It finds the NEIGHBOURHOOD -- on_valid / on_invalid / on_validated are all
    # reported on Select -- but not the members the user actually asked for.
    #
    # Asserting the miss is what stops a later session reading a quiet Select
    # row as "validation parity is fine". A scan's blind spot has to be louder
    # than its output.
    for member in ("valid", "error"):
        seen = member in sel
        print("  arm3 KNOWN LIMIT: scan misses Select.%-6s -> %s"
              % (member, "still missed (expected)" if not seen
                 else "NOW VISIBLE -- update this arm"))
        if seen:
            ok = False

    print()
    print("  control %s" % ("PASSED" if ok else "FAILED"))
    print()
    print("  Scope of the claim: this arm proves the scan finds ONE-HOP public")
    print("  members. It proves NOTHING about capabilities held deeper, which")
    print("  is the class #465 belongs to.")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("scan", "control"), default="scan")
    args = ap.parse_args()
    try:
        import bootstack  # noqa: F401
    except ImportError as exc:
        print("SKIP: bootstack did not import (%s)" % exc)
        return 0
    return control() if args.arm == "control" else scan()


if __name__ == "__main__":
    sys.exit(main())
