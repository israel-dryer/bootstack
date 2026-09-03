"""#468 -- a Select with allow_custom_values=True hands rules the raw typed text.

Two fields, the SAME `range` rule (5..10). The NumberField is the control: it is
what the rule is supposed to do. The Select disagrees with it on every value the
option list does not contain.

Type a value into each, then Tab out (`range` triggers on blur), or press
"Validate both". The readout shows what the rule actually received.

  '6'       -> the control accepts it, the Select rejects it   <- THE DEFECT
  '99'      -> both reject it, but the Select rejects it for the wrong reason
  'banana'  -> the Select rejects it, indistinguishably from '6'
  'Seven'   -> the Select accepts it: the lookup HIT, so the rule saw int 7

The NumberField refuses non-numeric keystrokes, so it stays EMPTY for the last
two and its rule passes vacuously (an empty field is not out of range). Read the
control column only on the numeric rows -- it is the '6' row that matters.

Reaching into `_get_validation_value()` is deliberate -- it is the seam every
field's public `validate()` reads, and the one `Select` overrides. There is no
public way to ask a field what its rule was handed.
"""

import bootstack as bs

OPTIONS = [("One", 1), ("Seven", 7), ("Twelve", 12)]

with bs.App(title="#468 -- Select validation sees text, not a value", padding=16, gap=12) as app:
    bs.Label("A range rule of 5..10 on two fields", font="heading-md")
    bs.Label(
        "Both carry the identical rule. Type the same thing into each and Tab out.",
        font="caption", accent="secondary",
    )

    with bs.Row(gap=24, horizontal="stretch"):
        with bs.Column(gap=6):
            bs.Label("Select(allow_custom_values=True)", font="body[bold]")
            select = bs.Select(
                options=OPTIONS,
                allow_custom_values=True,
                message="must be between 5 and 10",
                width=24,
            )
            select_readout = bs.Label("rule received: --", font="code", accent="secondary")

        with bs.Column(gap=6):
            bs.Label("NumberField  (the CONTROL)", font="body[bold]")
            number = bs.NumberField(message="must be between 5 and 10", width=24)
            number_readout = bs.Label("rule received: --", font="code", accent="secondary")

    select.add_validation_rule("range", min=5, max=10, message="must be between 5 and 10")
    number.add_validation_rule("range", min=5, max=10, message="must be between 5 and 10")

    def describe(field):
        # The one seam every field's public validate() reads. Select overrides it.
        received = field._internal._entry._get_validation_value()
        verdict = "VALID" if field.valid() else "INVALID"
        return "rule received: %r (%s)  ->  %s" % (received, type(received).__name__, verdict)

    def refresh():
        select_readout.text = describe(select)
        number_readout.text = describe(number)

    def validate_both():
        select.validate()
        number.validate()
        refresh()

    def try_value(text):
        def run():
            select._internal.entry_widget.delete(0, "end")
            select._internal.entry_widget.insert(0, text)
            number._internal.entry_widget.delete(0, "end")
            number._internal.entry_widget.insert(0, text)
            validate_both()
        return run

    select.on_validate(lambda e: refresh())
    number.on_validate(lambda e: refresh())

    bs.Divider()
    bs.Label(
        "Fill both fields with:   (the control only accepts numeric keystrokes, "
        "so it stays empty for the last two)",
        font="caption", accent="secondary",
    )
    with bs.Row(gap=8, horizontal="stretch"):
        bs.Button("6  (in range)", on_click=try_value("6"), accent="primary")
        bs.Button("99  (out of range)", on_click=try_value("99"))
        bs.Button("banana  (not a number)", on_click=try_value("banana"))
        bs.Button("Seven  (names an option)", on_click=try_value("Seven"))
        bs.Button("Validate both", on_click=validate_both, accent="secondary")

app.run()
