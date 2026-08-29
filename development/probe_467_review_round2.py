"""#467 review round 2 -- the four measurements the round turns on.

Scope is the FIX DIFF (`git diff 8b8e0964..HEAD`), so the control arm is the
branch's own pre-fix commit `8b8e0964`, NOT `main`. Run the control from a
worktree with PYTHONPATH set; the probe prints which arm it is on by reading
`validation_rules.py`, and prints its provenance.

    .venv/bin/python development/probe_467_review_round2.py
    PYTHONPATH=<worktree>/src .venv/bin/python development/probe_467_review_round2.py

Arms:
  1  a non-str `message` on the raise path        -- does the guard still hold?
  2  BOOTSTACK_DEBUG=1 and the one-shot test      -- is the stderr channel quiet?
  3  a broken stderr with BOOTSTACK_DEBUG=1       -- does the traceback survive?
  4  `warnings.warn` under -W error               -- why the channel is a print

Arm 1 needs its control to mean anything: the SAME non-str message on a genuine
verdict (the func returns False rather than raising) must pass through untouched
on both arms, or the arm is measuring `ValidationResult` rather than the guard.
"""
import io
import os
import subprocess
import sys
import warnings

import bootstack
from bootstack.validation.validation_rules import ValidationRule

PKG = os.path.dirname(bootstack.__file__)
SRC = os.path.join(PKG, "validation", "validation_rules.py")
ARM = "POST-FIX (branch)" if "_uncheckable_message" in open(SRC).read() else "PRE-FIX (8b8e0964)"

print(f"provenance: {PKG}")
print(f"ARM: {ARM}\n")


def rule(message, func=lambda v: v > 5):
    return ValidationRule("custom", func=func, message=message)


# --- arm 1: a non-str message on the raise path -----------------------------

print("arm 1  a non-str `message`, on the RAISE path")
for label, msg in [("None", None), ("'' (empty)", ""), ("str", "must exceed 5"),
                   ("int 42", 42), ("bytes", b"nope"), ("list", ["a"])]:
    try:
        res = rule(msg).validate("6")
        print(f"    {label:14} -> is_valid={res.is_valid} message={res.message!r}")
    except BaseException as exc:
        print(f"    {label:14} -> *** ESCAPED THE GUARD *** "
              f"{type(exc).__name__}: {exc}")

print("\narm 1  CONTROL -- the same messages on a genuine VERDICT (func returns False)")
print("       these must be identical on both arms, or the arm is measuring the")
print("       result object rather than the composer")
for label, msg in [("int 42", 42), ("bytes", b"nope"), ("str", "must exceed 5")]:
    try:
        res = rule(msg, func=lambda v: False).validate("6")
        print(f"    {label:14} -> is_valid={res.is_valid} message={res.message!r}")
    except BaseException as exc:
        print(f"    {label:14} -> RAISED {type(exc).__name__}: {exc}")


# --- arm 2: the test file under the env var its own message advertises ------

print("\narm 2  the test file, with and without BOOTSTACK_DEBUG=1")
print("       the new stderr line tells the author to set it; the suite must")
print("       survive them doing so")
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
target = os.path.join(here, "tests", "widgets", "public", "test_custom_rule_exception.py")
if os.path.exists(target):
    for env_label, debug in [("unset", None), ("BOOTSTACK_DEBUG=1", "1")]:
        env = dict(os.environ)
        env.pop("BOOTSTACK_DEBUG", None)
        if debug:
            env["BOOTSTACK_DEBUG"] = debug
        out = subprocess.run(
            [sys.executable, "-m", "pytest", target, "-q", "--no-header", "-p", "no:cacheprovider"],
            capture_output=True, text=True, env=env, cwd=here,
        )
        tail = [ln for ln in out.stdout.splitlines() if "passed" in ln or "failed" in ln]
        print(f"    {env_label:18} -> {tail[-1] if tail else '(no summary)'}")
else:
    print("    SKIP: test file not present on this arm")


# --- arm 3: a broken stderr, with the traceback explicitly asked for --------

print("\narm 3  BOOTSTACK_DEBUG=1 with a stderr whose write() raises")
print("       (a console redirected into a widget that has since been destroyed)")


class DeadStream:
    def write(self, _):
        raise RuntimeError("stream is closed")

    def flush(self):
        pass


def run_with_streams(err_stream):
    """Validate once, returning (result, what stdout got, what stderr got)."""
    os.environ["BOOTSTACK_DEBUG"] = "1"
    real_out, real_err = sys.stdout, sys.stderr
    out = io.StringIO()
    sys.stdout, sys.stderr = out, err_stream
    try:
        res = rule("m").validate("6")
    finally:
        sys.stdout, sys.stderr = real_out, real_err
        os.environ.pop("BOOTSTACK_DEBUG", None)
    return res, out.getvalue()


res, out = run_with_streams(DeadStream())
print(f"    guard held: {res.is_valid is False}")
print(f"    debug context line on the WORKING stream (stdout): {out!r}")

res, out = run_with_streams(io.StringIO())
print("    CONTROL, a working stderr:")
print(f"    debug context line on stdout: {out!r}")


# --- arm 4: why the channel is a bare print and not warnings.warn -----------

print("\narm 4  `warnings.warn` -- the framework's existing default-visible author")
print("       channel (style/fonts.py, _runtime/toplevel.py, data/_observable.py)")
print("       -- under -W error, at a site that runs inside a Tk dispatch")
warnings.simplefilter("error")
try:
    warnings.warn("bootstack: a 'custom' rule's func raised", RuntimeWarning)
    print("    unwrapped warn -> returned normally")
except Exception as exc:
    print(f"    unwrapped warn -> RAISES {type(exc).__name__}: it would escape the")
    print("                      guard and re-open #467 on the automatic trigger")
try:
    try:
        warnings.warn("bootstack: a 'custom' rule's func raised", RuntimeWarning)
    except Exception:
        pass
    print("    wrapped warn   -> swallowed: SILENT for exactly the developer who")
    print("                      runs with strict warnings")
finally:
    warnings.resetwarnings()

print("\n    the shipped print, same conditions:")
sys.stderr.write("    (this line is the print's channel, and -W error does not touch it)\n")
