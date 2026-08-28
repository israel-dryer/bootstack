"""#460 -- which public `.signal` properties can actually return None?

Constructs every widget that exposes a public `signal` property with NOTHING
bound, and reports what the property returns. A widget whose annotation says
`| None` but which never produces one is the defect.

Arms:
  scan     -- construct each widget unbound, report the value and the annotation
  control  -- bind a signal to each widget and confirm the property returns THAT
              signal, so a "LIVE" row in `scan` cannot be an artifact of the
              probe reading the wrong attribute

Run: py -3.12 development/probe_460_signal_never_none.py [--arm scan|control]
"""

import argparse
import inspect

import bootstack as bs

# (label, factory, kwarg name used to bind a signal, a value the widget accepts)
CASES = [
    ("TextField", lambda **kw: bs.TextField(**kw), "textsignal", ""),
    ("PasswordField", lambda **kw: bs.PasswordField(**kw), "textsignal", ""),
    ("PathField", lambda **kw: bs.PathField(**kw), "textsignal", ""),
    ("SpinnerField", lambda **kw: bs.SpinnerField(**kw), "textsignal", ""),
    ("SelectButton", lambda **kw: bs.SelectButton(options=["a", "b"], **kw), "signal", "a"),
    ("Checkbox", lambda **kw: bs.Checkbox("c", **kw), "signal", False),
    ("Switch", lambda **kw: bs.Switch("s", **kw), "signal", False),
    ("ToggleButton", lambda **kw: bs.ToggleButton("t", **kw), "signal", False),
    ("TextArea", lambda **kw: bs.TextArea(**kw), "textsignal", ""),
    ("CodeEditor", lambda **kw: bs.CodeEditor(**kw), "textsignal", ""),
    ("Slider", lambda **kw: bs.Slider(**kw), "signal", 0.0),
    ("NumberField", lambda **kw: bs.NumberField(**kw), "signal", 0),
    ("DateField", lambda **kw: bs.DateField(**kw), "signal", None),
    ("TimeField", lambda **kw: bs.TimeField(**kw), "signal", None),
    ("Select", lambda **kw: bs.Select(options=["a", "b"], **kw), "signal", "a"),
]


def annotation_of(obj):
    """Return the declared return annotation of the public `signal` property."""
    prop = type(obj).__dict__.get("signal")
    if prop is None:
        for base in type(obj).__mro__:
            prop = base.__dict__.get("signal")
            if prop is not None:
                break
    if prop is None or not isinstance(prop, property):
        return "(no property)"
    fn = prop.fget
    ann = inspect.signature(fn).return_annotation
    if ann is inspect.Signature.empty:
        return "(unannotated)"
    return str(ann).strip("'\"")


def run(arm):
    rows = []
    with bs.App(title="probe 460") as app:
        for label, factory, kwname, seed in CASES:
            try:
                if arm == "control":
                    sig = bs.Signal(seed)
                    w = factory(**{kwname: sig})
                else:
                    sig = None
                    w = factory()
            except Exception as exc:  # noqa: BLE001 -- report, never abort the sweep
                rows.append((label, "BUILD FAILED: %s" % exc, "", ""))
                continue

            got = getattr(w, "signal", "(no public .signal)")
            ann = annotation_of(w)
            if got is None:
                shown = "None"
            elif isinstance(got, str):
                shown = got
            else:
                shown = "LIVE Signal(%r)" % (got(),)

            if arm == "control":
                verdict = "OK" if got is sig else "*** NOT THE BOUND SIGNAL ***"
            else:
                claims_none = "None" in ann
                if got is None:
                    verdict = "ok" if claims_none else "*** RETURNS None, ANNOTATION DOES NOT ***"
                else:
                    verdict = "*** DEFECT: never None ***" if claims_none else "ok"
            rows.append((label, shown, ann, verdict))

    width = max(len(r[0]) for r in rows)
    vwidth = max(len(r[1]) for r in rows)
    print("arm: %s" % arm)
    print("-" * 100)
    for label, shown, ann, verdict in rows:
        print("%-*s  %-*s  %-28s  %s" % (width, label, vwidth, shown, ann, verdict))
    print("-" * 100)
    defects = [r[0] for r in rows if r[3].startswith("***")]
    print("flagged: %d -- %s" % (len(defects), ", ".join(defects) if defects else "(none)"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("scan", "control"), default="scan")
    run(ap.parse_args().arm)
