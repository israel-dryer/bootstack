"""Can `event.widget` in a dialog ever be a bare string instead of a widget?

`press_default` reads bindtags to decide whether a button already handled the
key. Reading them off the widget (`event.widget.bindtags()`) is the obvious
spelling; going through Tcl (`tk.call("bindtags", event.widget)`) is only
warranted if the callback can be handed a path STRING, which Tkinter does
whenever the target is absent from its widget map:

    try:                                    # CPython, tkinter/__init__.py
        e.widget = self._nametowidget(W)
    except KeyError:
        e.widget = W

So the question is whether a dialog can contain such a widget. This walks every
descendant straight from Tcl -- not from Tkinter's map, which would beg the
question -- and asks Tkinter to resolve each one.

The CONTROL matters here: a probe that reports "none found" is worthless unless
it can find one. So it also creates a genuinely map-absent widget by calling
Tcl directly, and confirms the same check flags it.

Run: py -3.13 development/probe_437_bindtags_via_widget.py
"""

import bootstack as bs
from bootstack.dialogs import Dialog, DialogButton

app = bs.App(title="probe", size=(320, 120))


def build():
    bs.Label("Name")
    bs.TextField()
    bs.Select(options=[("A", "a"), ("B", "b")])
    bs.DateField()
    bs.TextArea(height=3)


dlg = Dialog(
    title="probe",
    content_builder=build,
    buttons=[
        DialogButton("Save", role="primary", result="save", default=True),
        DialogButton("Cancel", role="cancel"),
    ],
)

result = {}


def walk(top, path):
    """Every descendant path, straight from Tcl -- not from Tkinter's map."""
    out = [path]
    for child in top.tk.splitlist(top.tk.call("winfo", "children", path)):
        out.extend(walk(top, str(child)))
    return out


def unresolvable(top, paths):
    """The paths Tkinter cannot turn into a widget -- i.e. the string cases."""
    missing = []
    for p in paths:
        try:
            top.nametowidget(p)
        except KeyError:
            missing.append(p)
    return missing


def drive():
    top = dlg._toplevel
    paths = walk(top, str(top))
    result["total"] = len(paths)
    result["missing"] = unresolvable(top, paths)

    # Control: a widget created by Tcl directly never enters Tkinter's map, so
    # the detector above must flag it. If this comes back empty the probe cannot
    # find anything and its main result means nothing.
    top.tk.call("ttk::button", str(top) + ".tclmade", "-text", "x")
    control_path = str(top) + ".tclmade"
    result["control"] = unresolvable(top, [control_path])
    result["control_tags"] = top.tk.splitlist(top.tk.call("bindtags", control_path))

    top.destroy()


guard = app.tk.after(8000, lambda: dlg._toplevel.destroy())
try:
    app.tk.after(400, drive)
    dlg.show()
finally:
    app.tk.after_cancel(guard)

print("descendants of a dialog holding TextField/Select/DateField/TextArea: %d" % result["total"])
print("of those, absent from Tkinter's widget map: %d" % len(result["missing"]))
for p in result["missing"]:
    print("   %s" % p)

print()
print("control -- a Tcl-created ttk::button, flagged as absent: %s"
      % (len(result["control"]) == 1))
print("control -- its bindtags, read through Tcl: %s" % (result["control_tags"],))

if not result["control"]:
    print("\nINCONCLUSIVE: the detector found nothing even in the control.")
elif result["missing"]:
    print("\nVERDICT: the string case IS reachable -- keep the Tcl call.")
else:
    print("\nVERDICT: no string case in a dialog -- `event.widget.bindtags()` is enough.")

app.tk.destroy()
