"""Does Enter inside a dialog's TextArea submit the dialog instead of newlining?

The toplevel Enter binding stands down for a button, because a button has
already handled the key. A TextArea handles Enter too -- it inserts a newline --
but carries no `TButton` tag, so the guard does not recognize it and the default
button fires on top: the dialog closes mid-paragraph and the newline is lost.

Control: the same press in a single-line TextField, which does NOT handle Enter,
where firing the default button is the whole point of the binding.

Run: py -3.13 development/probe_437_enter_in_a_textarea.py
"""

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton

app = bs.App(title="probe", size=(320, 120))

results = {}


def run(kind):
    """Open a dialog whose body is `kind`, press Enter in it, report."""
    holder = {}

    def build():
        if kind == "textarea":
            holder["w"] = bs.TextArea(height=4)
        else:
            holder["w"] = bs.TextField()

    calls = []

    def on_ok(d):
        # Read while the content is still alive -- after the dialog closes the
        # widget is destroyed and the text is unreachable either way.
        calls.append("ok")
        holder["at_press"] = holder["w"].value

    dlg = Dialog(
        title=kind,
        content_builder=build,
        buttons=[DialogButton(
            text="OK", role="primary", result="ok", default=True,
            command=on_ok,
        )],
        parent=app.tk,
    )

    def drive():
        top = dlg._toplevel
        pub = holder["w"]
        w = pub.tk           # the widget the key is actually delivered to
        w.focus_set()
        before = pub.value
        w.event_generate("<Return>", when="now")

        closed = not top.winfo_exists()
        after = None
        if not closed:
            after = pub.value
            top.destroy()
        results[kind] = {
            "calls": list(calls),
            "closed_by_the_key": closed,
            "text_before": before,
            "text_at_press": holder.get("at_press"),
            "text_after": after,
        }

    guard = app.tk.after(6000, lambda: dlg._toplevel.destroy())
    try:
        app.tk.after(400, drive)
        dlg.show()
    finally:
        app.tk.after_cancel(guard)


run("textarea")
run("textfield")

for kind in ("textarea", "textfield"):
    r = results[kind]
    print("%s:" % kind)
    print("   default button ran: %s" % (r["calls"],))
    print("   dialog closed on the key: %s" % r["closed_by_the_key"])
    print("   text before=%r  at the press=%r  after=%r"
          % (r["text_before"], r["text_at_press"], r["text_after"]))

ta = results["textarea"]
tf = results["textfield"]
print()
if ta["closed_by_the_key"]:
    print("REPRODUCED: Enter in a TextArea submitted the dialog instead of newlining.")
    print("            The text area held %r at the press -- so the newline %s,"
          % (ta["text_at_press"],
             "WAS inserted first" if ta["text_at_press"] != ta["text_before"]
             else "never landed"))
    print("            and the dialog closed on top of it either way.")
else:
    print("NOT reproduced for the TextArea.")
print("control -- TextField submits, which is the binding working as intended: %s"
      % (tf["calls"] == ["ok"],))

app.tk.destroy()
