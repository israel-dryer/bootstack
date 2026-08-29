"""#467 -- a `custom` rule whose predicate cannot handle the value it is given.

Run it:  .venv/bin/python development/demo_467_custom_rule_exception.py
Drive it headlessly:  .venv/bin/python development/probe_467_demo_driver.py \
                          development/demo_467_custom_rule_exception.py

THE POINT. A `custom` rule hands your predicate the field's TYPED VALUE, and the
type depends on the widget. Get that pairing wrong and your predicate raises --
it never judges the value at all. This is what each field actually passes, and
what each predicate does with it (measured, not guessed):

    a TextField passes:      '6'        'abc'       None (when empty)
      v > 5                  RAISED     RAISED      RAISED
      int(v) > 5             valid      RAISED      RAISED
      not v or int(v) > 5    valid      RAISED      valid
      not v or (v.isdigit() and int(v) > 5)
                             valid      invalid     valid     <- handles all three

    a NumberField passes:    6          4           0 (its empty)
      v > 5                  valid      invalid     invalid   <- no conversion needed

So there are two right answers, and panels 3 and 4 are each one of them: guard
the predicate for the type your field passes, or pick the field whose type your
predicate already wants. The guard this branch adds is the safety net for when
you do neither -- it is not a substitute for either.

WHAT TO LOOK FOR. The console at the bottom mirrors stderr.

  1. WRONG TYPE     `v > 5` on a TextField. Even "6" raises -- it is the STRING
                    '6', and a str cannot be compared to an int. The field says
                    "Could not check this value (expected: must be over 5)" --
                    the rule's message carried as an EXPECTATION, not asserted as
                    a verdict about a value nothing ever checked. Compare panel 3,
                    where a real failure shows "must be over 5" on its own.
                    Type several letters: the console gets ONE
                    line, not one per keystroke. On `main` this field reports
                    valid forever and never validates again -- that is the defect.

  2. CONVERTS       `int(v) > 5`. Judges "6" correctly. Type "abc", or clear the
                    field: both raise, because int() cannot take either and an
                    empty text field passes None, not ''.

  3. GUARDED        `not v or (v.isdigit() and int(v) > 5)`. Every input gets a
                    verdict, the console stays silent, and a real failure shows
                    the rule's OWN message. This is the predicate to write.

  4. RIGHT TYPE     `v > 5` on a NumberField, which passes a real number. No
                    conversion, nothing to guard, console silent. Often the
                    better fix: change the field, not the predicate.

  5. MANUAL         Press Validate. Returns False rather than raising. This path
                    matters more than it looks: `FormDialog`'s submit button
                    reaches it with the DEFAULT trigger -- no `trigger=` anywhere
                    -- so on `main` the press did nothing and the dialog just sat
                    there.

Panels 3 and 4 are also the control: they are identical on `main` and on this
branch. A predicate that never raises is untouched by any of this, which is what
makes the difference in panels 1, 2 and 5 the guard rather than the instrument.

SEEING THE BEFORE:

    git worktree add /tmp/bs-main main
    PYTHONPATH=/tmp/bs-main/src .venv/bin/python \
        development/demo_467_custom_rule_exception.py
"""
import sys

import bootstack as bs

WRONG_TYPE = lambda v: v > 5                                   # str vs int
CONVERTS = lambda v: int(v) > 5                                # ok for '6' only
GUARDED = lambda v: not v or (v.isdigit() and int(v) > 5)      # handles all three
RIGHT_TYPE = lambda v: v > 5                                   # on a NumberField


class _Tee:
    """Mirror stderr into the on-screen console without swallowing it."""

    def __init__(self, real, sink):
        self._real = real
        self._sink = sink

    def write(self, text):
        self._real.write(text)
        if text.strip():
            self._sink(text.rstrip("\n"))
        return len(text)

    def flush(self):
        self._real.flush()


def build():
    """Build the window and return it with the fields, so a driver can drive it."""
    log = bs.Signal("(quiet -- nothing has raised yet)")
    lines: list[str] = []

    def append(text: str) -> None:
        lines.append(text)
        log.set("\n\n".join(lines[-3:]))

    with bs.App(title="#467 -- a predicate that cannot judge its value",
                size=(800, 940), padding=16, gap=10) as app:
        bs.Label("Match the predicate to the type the field passes it",
                 font="heading-md")
        bs.Label(
            "A `custom` rule hands your predicate the field's TYPED value. A TextField "
            "passes text -- and None when it is empty. A NumberField passes a number. "
            "Pair them wrong and the predicate raises instead of judging.",
            wrap_width=740, accent="muted",
        )
        bs.Label(
            "When it raises, the field says \"Could not check this value (expected: "
            "must be over 5)\" -- your message carried as an EXPECTATION, not asserted "
            "as a verdict about a value nothing ever checked. Panels 3 and 4 never "
            "raise, and show that message on its own when they genuinely say no.",
            wrap_width=740, accent="warning",
        )

        with bs.Card(gap=6):
            bs.Label("1. Wrong type -- `v > 5` on a TextField", font="body+1[bold]")
            bs.Label("Tab away. Even \"6\" raises: it is the string '6'. Then type "
                     "several letters -- the console gets ONE line, not one per "
                     "keystroke.",
                     wrap_width=720, accent="muted")
            wrong = bs.TextField(value="6", label="TextField, unconverted")
            wrong.add_validation_rule("custom", func=WRONG_TYPE, trigger="always",
                                      message="must be over 5")

        with bs.Card(gap=6):
            bs.Label("2. Converts, but not for everything -- `int(v) > 5`",
                     font="body+1[bold]")
            bs.Label("Tab away with \"6\": valid, correctly. Now try \"abc\", then "
                     "clear the field. Both raise -- an empty TextField passes None.",
                     wrap_width=720, accent="muted")
            converts = bs.TextField(value="6", label="TextField, int()")
            converts.add_validation_rule("custom", func=CONVERTS, trigger="blur",
                                         message="must be over 5")

        with bs.Card(gap=6):
            bs.Label("3. Guarded -- `not v or (v.isdigit() and int(v) > 5)`",
                     font="body+1[bold]")
            bs.Label("Try \"6\", \"abc\", \"2\", and empty. Every one gets a verdict, "
                     "the console stays silent, and a real failure shows the RULE'S "
                     "own message. This is the predicate to write.",
                     wrap_width=720, accent="muted")
            guarded = bs.TextField(value="6", label="TextField, guarded")
            guarded.add_validation_rule("custom", func=GUARDED, trigger="always",
                                        message="must be over 5")

        with bs.Card(gap=6):
            bs.Label("4. Right type -- `v > 5` on a NumberField", font="body+1[bold]")
            bs.Label("The field passes a real number, so the original predicate works "
                     "as written. Nothing to convert, nothing to guard. Often the "
                     "better fix: change the field, not the predicate.",
                     wrap_width=720, accent="muted")
            right = bs.NumberField(value=6, label="NumberField")
            right.add_validation_rule("custom", func=RIGHT_TYPE, trigger="always",
                                      message="must be over 5")

        with bs.Card(gap=6):
            bs.Label("5. The manual path -- validate() from a button",
                     font="body+1[bold]")
            bs.Label("Before the fix this RAISED out of the handler. FormDialog's "
                     "submit reaches this path with the DEFAULT trigger, so the press "
                     "did nothing at all.",
                     wrap_width=720, accent="muted")
            manual = bs.TextField(value="abc", label="Manual only")
            manual.add_validation_rule("custom", func=CONVERTS,
                                       message="must be over 5")
            manual_result = bs.Signal("not run yet")

            def run_manual() -> None:
                try:
                    manual_result.set(f"validate() returned {manual.validate()!r}")
                except Exception as exc:                     # noqa: BLE001
                    manual_result.set(f"validate() RAISED {type(exc).__name__}: {exc}")

            with bs.Row(gap=8, vertical_items="center"):
                bs.Button("Validate", on_click=run_manual, accent="primary")
                bs.Label(textsignal=manual_result)

        bs.Label("Console (mirrors stderr)", font="body+1[bold]")
        bs.Label(textsignal=log, wrap_width=740, font="code")

    sys.stderr = _Tee(sys.stderr, append)
    return app, {
        "wrong": wrong,
        "converts": converts,
        "guarded": guarded,
        "right": right,
        "manual": manual,
        "manual_result": manual_result,
        "log": log,
    }


def main() -> None:
    real_stderr = sys.stderr
    app, _ = build()
    try:
        app.run()
    finally:
        sys.stderr = real_stderr


if __name__ == "__main__":
    main()
