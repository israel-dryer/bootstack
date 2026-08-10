"""Controls for the round-2 review fixes: every new test observed failing.

Reverts one fix at a time, in place, runs the test that names it, and restores
the file. A test that cannot be seen failing proves nothing, and this repo has
shipped two vacuous tests (#417) plus one more caught by its own control (#437)
without them.

    py -3.12 development/probe_437_review2_controls.py

Two things this does deliberately:

- **Each revert ASSERTS it matched.** A scripted revert that silently matches
  nothing produces a "control" showing a passing test against fixed source. The
  #438 controls hit exactly that: these sources are CRLF while the test files
  are LF, so a pattern written with `\\n` matched nothing.
- **The two rewritten-but-unchanged paths get sensitivity controls instead of
  reverts.** `query._on_submit` and `datedialog._on_confirm_range` were rewritten
  onto the #437 veto without changing behavior, so there is no fix to revert;
  what their new tests must prove is that they would notice if the accept or the
  refuse arm broke. So each is broken in both directions.

Output is ASCII only (#430: a check mark raises UnicodeEncodeError on a cp1252
console).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "bootstack"
TESTS = "tests/widgets/public"

FORMDIALOG = SRC / "dialogs" / "_impl" / "formdialog.py"
DIALOG = SRC / "dialogs" / "_impl" / "dialog.py"
QUERY = SRC / "dialogs" / "_impl" / "query.py"
DATEDIALOG = SRC / "dialogs" / "_impl" / "datedialog.py"
FORM = SRC / "widgets" / "_impl" / "composites" / "form.py"

PRESS = f"{TESTS}/test_dialog_press_contract.py"
RESULT = f"{TESTS}/test_formdialog_result_value.py"


def crlf(text: str) -> bytes:
    """Encode with CRLF, matching every file under `src/` in this repo."""
    return text.replace("\n", "\r\n").encode("utf-8")


# (label, file, revert-from, revert-to, test node id)
CASES = [
    (
        "F1  Form discards the command's return value",
        FORM,
        """            if spec.command and spec.command(self) is False:  # type: ignore[arg-type]
                return
""",
        """            if spec.command:
                spec.command(self)  # type: ignore[arg-type]
""",
        f"{PRESS}::test_a_form_button_command_can_refuse_its_press",
    ),
    (
        "F3  the role wins over the result token",
        FORMDIALOG,
        """        if isinstance(btn.result, str) and btn.result.lower() in self._DATA_RESULTS:
            return True
        if btn.role == "cancel":
            return False
""",
        """        if btn.role == "cancel":
            return False
        if isinstance(btn.result, str) and btn.result.lower() in self._DATA_RESULTS:
            return True
""",
        f"{RESULT}::test_a_cancel_role_button_carrying_a_data_token_captures_its_own_run",
    ),
    (
        "F8  a bad mapping raises a bare TypeError",
        FORMDIALOG,
        """                try:
                    normalized.append(DialogButton(**btn))
                except TypeError as exc:
                    raise ValueError(f"Invalid button mapping {btn!r}: {exc}") from exc
""",
        """                normalized.append(DialogButton(**btn))
""",
        f"{RESULT}::test_a_removed_kwarg_names_the_button_it_came_from",
    ),
    (
        "F4  only Return is bound, not the keypad key",
        DIALOG,
        """            for key in ("<Return>", "<KP_Enter>"):
                self._toplevel.bind(key, lambda e, b=default_button: b.invoke())
""",
        """            self._toplevel.bind("<Return>", lambda e, b=default_button: b.invoke())
""",
        f"{PRESS}::test_the_keypad_enter_key_is_bound_alongside_enter",
    ),
    # --- sensitivity, not reverts: these paths were rewritten, not changed ---
    (
        "F5  QueryDialog accepts a submit it should refuse",
        QUERY,
        """            if result is None:
                return False
""",
        """            if result is None:
                return True
""",
        f"{PRESS}::test_query_dialog_refuses_a_submit_it_cannot_accept",
    ),
    (
        "F5  QueryDialog refuses a submit it should accept",
        QUERY,
        """            self._dialog.result = result
            return True
""",
        """            self._dialog.result = result
            return False
""",
        f"{PRESS}::test_query_dialog_submit_records_the_value_and_closes",
    ),
    (
        "F5  DateDialog accepts an incomplete range",
        DATEDIALOG,
        """        if start is None or end is None:
            return False
""",
        """        if start is None or end is None:
            return True
""",
        f"{PRESS}::test_date_range_ok_is_refused_until_both_endpoints_are_picked",
    ),
    (
        "F5  DateDialog refuses a complete range",
        DATEDIALOG,
        """        self._record((start, end))
        return True
""",
        """        self._record((start, end))
        return False
""",
        f"{PRESS}::test_date_range_ok_returns_both_endpoints_and_closes",
    ),
]


def run_one(label, path, before, after, node_id) -> str:
    original = path.read_bytes()
    old, new = crlf(before), crlf(after)
    count = original.count(old)
    if count != 1:
        return f"SETUP FAILED - the revert pattern matched {count} times, expected 1"

    path.write_bytes(original.replace(old, new))
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", node_id, "-q", "--no-header"],
            cwd=ROOT, capture_output=True, text=True,
        )
    finally:
        path.write_bytes(original)
        assert path.read_bytes() == original, f"FAILED TO RESTORE {path}"

    if proc.returncode == 0:
        tail = proc.stdout.strip().splitlines()[-1:] or [""]
        return f"PASSED against reverted logic - THE TEST PROVES NOTHING ({tail[0]})"

    reason = ""
    for line in proc.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("E ") and "assert" not in stripped[:8]:
            reason = stripped[2:].strip()
            break
    return f"FAIL (correct) - {reason[:90]}" if reason else "FAIL (correct)"


if __name__ == "__main__":
    print("Reverting each fix in place and running the test that names it.\n")
    verdicts = []
    for label, path, before, after, node_id in CASES:
        outcome = run_one(label, path, before, after, node_id)
        verdicts.append(outcome.startswith("FAIL (correct)"))
        print(f"  {label}")
        print(f"      -> {outcome}\n")

    ok = all(verdicts)
    print("ALL CONTROLS BEHAVED" if ok else "SOME CONTROLS DID NOT FAIL - INVESTIGATE")
    sys.exit(0 if ok else 1)
