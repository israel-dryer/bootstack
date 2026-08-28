"""#486 demo -- two-way `textsignal` binding on TextArea / CodeEditor.

Run it and watch the readouts under each widget. The signal readout is a real
subscriber on the bound signal, so it moves only when the signal actually moves.

WHAT TO TRY

1. Click into the multi-line box and type. `signal` follows every keystroke.
   Before #486 it never moved at all -- the binding only ran signal -> widget.

2. Select all, delete, then press Tab to leave the field. The grey placeholder
   appears. `signal` must stay '' and `value` must stay ''.
   Before the round 1 fix the signal became 'Type something here' -- the widget
   put its own UI chrome into your data.

3. WITH THE PLACEHOLDER STILL SHOWING, press "set from code". The text must
   appear, and all three of screen, `value` and `signal` must read
   'written by code'. An earlier version of the fix REVERTED this write: the
   widget answered "" for its own text while the placeholder flag was up, and
   pushed that "" back over the caller's value. This demo is what caught it.

4. Press "clear the signals", then click in and type again. Everything should
   keep tracking.

5. The single-line TextField on the right is the shipped exemplar this pair was
   made to match. Do the same things to it.
   TWO KNOWN TEXTFIELD DIFFERENCES, NEITHER A BUG IN THIS WORK. Both are
   pre-existing, and this branch does not touch TextField at all.

   a) Its `value` readout does not move while you type -- it updates on blur or
      Enter. That is the field family's commit model: `value` is the committed
      datum, not the in-progress text. `TextArea.value` IS the live document, so
      it moves per keystroke. The two SIGNALS are identical -- both push on
      every keystroke -- which is the part #486 is about.

   b) After "set from code" its `value` readout says None while its screen and
      signal are both correct. That is #482, a field's `value` lagging a
      programmatic signal write until the next commit. Click into it and tab out
      and it catches up.

The `.signal` line at the bottom is the other half of #486: that property
returned None no matter what before, so there was no way to ask a widget what it
was bound to.
"""
import bootstack as bs
from bootstack.scheduling import Schedule

PLACEHOLDER = "Type something here"

area_signal = bs.Signal("hello")
field_signal = bs.Signal("hello")

# `value` is a plain property, not a signal, so these mirror it on a timer --
# the placeholder appears on blur, which is not a change event.
area_value = bs.Signal("")
field_value = bs.Signal("")

with bs.App(title="#486 -- two-way textsignal binding", size=(940, 620),
            padding=16, gap=12) as app:

    bs.Label("Two-way textsignal binding (#486)", font="heading-lg")
    bs.Label(
        "Type, then clear the field and press Tab: the placeholder appears and the "
        "signal must stay empty. Then press 'set from code' while it is showing.",
        font="caption",
    )
    bs.Divider()

    with bs.Row(gap=24, grow_items=True, vertical_items="start"):

        with bs.Column(gap=6):
            bs.Label("TextArea -- fixed here", font="heading-md")
            area = bs.TextArea(
                placeholder=PLACEHOLDER,
                textsignal=area_signal,
                height=8,
                show_border=True,
            )
            bs.Label(textsignal=area_signal.map(lambda v: "signal :  %r" % (v,)),
                     font="code")
            bs.Label(textsignal=area_value.map(lambda v: "value  :  %s" % (v,)),
                     font="code")

        with bs.Column(gap=6):
            bs.Label("TextField -- the shipped exemplar", font="heading-md")
            field = bs.TextField(
                placeholder=PLACEHOLDER,
                textsignal=field_signal,
            )
            bs.Label(textsignal=field_signal.map(lambda v: "signal :  %r" % (v,)),
                     font="code")
            bs.Label(textsignal=field_value.map(lambda v: "value  :  %s" % (v,)),
                     font="code")

    bs.Divider()

    with bs.Row(gap=8):
        bs.Button("set from code",
                  on_click=lambda: (area_signal.set("written by code"),
                                    field_signal.set("written by code")))
        bs.Button("clear the signals", variant="outline",
                  on_click=lambda: (area_signal.set(""), field_signal.set("")))

    bs.Label(
        ".signal identity -- area: %s   field: %s"
        % (area.signal is area_signal, field.signal is field_signal),
        font="code",
    )
    bs.Label(
        "Both must read True. Before #486 TextArea.signal returned None here.",
        font="caption",
    )
    bs.Label(
        "TextField readouts, both pre-existing and neither touched by this branch: "
        "its 'value' updates on blur or Enter rather than per keystroke (the field "
        "family's commit model -- the two SIGNALS are identical and both push per "
        "keystroke), and after 'set from code' it reads None until the next commit "
        "(#482).",
        font="caption",
        wrap_width=880,
    )


def _mirror() -> None:
    area_value.set(repr(area.value))
    field_value.set(repr(field.value))


_mirror()
Schedule(app).every(120, _mirror)

app.run()
