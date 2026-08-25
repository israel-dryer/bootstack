"""#383 gap 3 -- what does each public wrapper DO with an unrecognised keyword?

`PLAN.md` says to verify the fix with `probe_wrapper_parameter_delta.py --arm
leftovers`. That arm is the wrong instrument for a before/after: it compares the
STATIC verdict against actual construction, so once the seam guard lands every
wrapper whose source still looks like a dropper but now rejects reads as a
DISAGREE -- and that arm prints "a disagreement here is a defect in THIS PROBE".
It would report the fix as a tool bug.

This one classifies by CONSTRUCTION ONLY, which is what actually changed:

    dropped   -- constructed, the bogus name vanished          <- the defect
    rejected  -- raised, and the message NAMES the bogus key   <- the fix
    other     -- raised without naming it (a pre-existing raise, or a build
                 failure unrelated to the keyword)             <- not our signal

    py -3.12 development/probe_383_unknown_kwarg_policy.py [--arm ARM]

Arms:
    measure   the classification, printed per wrapper and summarised. Run it on
              `main` BEFORE the fix and on the branch after; diff the summaries.
    control   proves the probe can see BOTH outcomes, so a post-fix `dropped=0`
              is a measurement rather than an artifact of the probe being blind.
              Five wrappers reject an unknown keyword TODAY
              (`_BooleanControlBase`) and 40 drop it, so a healthy control is a
              non-empty count in each column on unmodified source.

Output is ASCII only (the Windows console is cp1252).
"""
import argparse

import bootstack as bs

BOGUS = "bogus_xyz_383"

# The 52 public wrappers carrying a **kwargs catch-all, from the #463 audit.
WRAPPERS = [
    "Accordion", "Avatar", "Badge", "Button", "ButtonGroup", "Calendar", "Card",
    "Carousel", "Chart", "Checkbox", "CodeEditor", "Column", "DataTable",
    "DateField", "Divider", "Form", "Gallery", "Gauge", "Grid", "GroupBox",
    "Label", "ListView", "MenuButton", "NumberField", "PageStack",
    "PasswordField", "PathField", "Picture", "ProgressBar", "Radio",
    "RadioGroup", "RadioToggleButton", "RangeSlider", "Row", "ScrollView",
    "Select", "SelectButton", "Slider", "SpinnerField", "SplitView",
    "StatusBar", "Switch", "Tabs", "TextArea", "TextField", "TimeField",
    "ToggleButton", "ToggleGroup", "Toolbar", "Tree",
]

# Deliberate forwarders -- they hand leftovers to the internal on purpose.
FORWARDERS = {"Chart", "MenuButton", "Picture", "StatusBar", "Toolbar"}


def classify(cls):
    """Construct with a bogus keyword and report what the wrapper did with it."""
    try:
        cls(**{BOGUS: 1})
    except Exception as exc:                    # noqa: BLE001 -- classified, not hidden
        return ("rejected" if BOGUS in str(exc) else "other",
                "%s: %s" % (type(exc).__name__, str(exc)[:70]))
    return ("dropped", "")


def measure(verbose=True):
    app = bs.App(title="probe-383")
    buckets = {"dropped": [], "rejected": [], "other": []}
    with app:
        for name in WRAPPERS:
            cls = getattr(bs, name, None)
            if cls is None:
                continue
            policy, detail = classify(cls)
            buckets[policy].append(name)
            if verbose:
                mark = " (forwarder)" if name in FORWARDERS else ""
                print("  %-20s %-9s%s %s" % (name, policy, mark, detail))
    print()
    print("  dropped=%d  rejected=%d  other=%d"
          % (len(buckets["dropped"]), len(buckets["rejected"]), len(buckets["other"])))
    if buckets["dropped"]:
        print("  still dropping: %s" % ", ".join(sorted(buckets["dropped"])))
    return buckets


def control():
    """Both outcomes must be observable, or a quiet `measure` means nothing."""
    buckets = measure(verbose=False)
    ok = bool(buckets["dropped"]) and bool(buckets["rejected"])
    print()
    print("CONTROL: the probe saw dropped=%d and rejected=%d."
          % (len(buckets["dropped"]), len(buckets["rejected"])))
    if ok:
        print("  OK -- both outcomes are observable, so a later dropped=0 is real.")
    else:
        print("  READ THIS BEFORE TRUSTING ANY OTHER RUN: only one outcome was")
        print("  seen. On UNMODIFIED source both must appear (5 boolean controls")
        print("  reject today, 40 wrappers drop). One-sided means the probe is")
        print("  blind, not that the code is clean.")
    return 0 if ok else 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="measure", choices=("measure", "control"))
    args = ap.parse_args()
    if args.arm == "control":
        raise SystemExit(control())
    measure()
    print()
    print("READING: `dropped` is #383 gap 3. The fix should move all 40 to")
    print("`rejected` and leave the 5 forwarders alone -- they are listed as")
    print("(forwarder) above and are expected to stay non-rejecting.")


if __name__ == "__main__":
    main()
