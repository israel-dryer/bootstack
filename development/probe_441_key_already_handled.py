"""Probe for #441 - what rule decides "something already handled Enter"?

`Dialog` binds Return/KP_Enter on the toplevel so the default button can be
pressed from an input field. That binding must stand down when something else
already answered the key; today it recognizes only buttons, via the `TButton`
bindtag. A `TextArea` answers Enter too and carries no such tag, so the newline
is inserted AND the dialog closes on top of it (#441).

The issue asks for a RULE rather than a second special case, and floats three.
This probe evaluates the two that stay internal, side by side, against the
population that actually appears in a dialog:

  RULE A  interrogate the bindtags - does any carry a real (non-no-op)
          binding for the key? The general-looking candidate.
  RULE B  a bindtag allowlist: `TButton` (already invoked) or `Text` (Enter
          is content there, not a command).

⚠ MEASURE INSIDE A `bs.App`. Raw tkinter reports that `TButton` has NO Return
binding, which would say the framework's guard rests on a false premise. It
does not: bootstack INSTALLS `TButton <Key-Return>` -> `button_default_binding`
at app construction (`_runtime/app.py:151`). Measuring raw ttk measures the
wrong population - the same error as comparing captures across two `bs.App`
instances.

⚠ THE KEY WIDGET IS NESTED. A `TextArea` is a `TFrame`; the widget the key is
delivered to is a `Text` four levels down (`!textarea > !frame >
!_multilinecore > !text`). Classifying the public wrapper measures a frame and
concludes, wrongly, that a text area does not answer Enter.

Run:  py -3.13 development/probe_441_key_already_handled.py
"""

from __future__ import annotations

import sys
import tkinter

import bootstack as bs

KEYS = ("<Return>", "<KP_Enter>")

# Bindtags whose widgets treat Enter as CONTENT rather than as a command.
# `Text` is Tk's multi-line text class, which is what TextArea and CodeEditor
# are built on, so the list covers both without naming either.
CONSUMES_ENTER = frozenset({"Text"})

failures: list[str] = []


def _is_noop_script(script: str) -> bool:
    """True if a Tcl binding script does nothing - only comments/whitespace.

    Tk binds `TEntry <Return>` to the literal script `# nothing`, its idiom for
    a deliberately empty binding.
    """
    for line in str(script).splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return False
    return True


def rule_a(widget, top) -> tuple[bool, list[str]]:
    """Does any of the widget's own bindtags really answer Return?"""
    hits: list[str] = []
    own = str(top)
    for tag in widget.bindtags():
        tag = str(tag)
        if tag in (own, "all"):
            continue
        for seq in KEYS:
            try:
                script = widget.bind_class(tag, seq)
            except tkinter.TclError:
                continue
            if not script:
                continue
            hits.append(f"{tag}{seq}" + ("=NOOP" if _is_noop_script(script) else ""))
    return any(not h.endswith("=NOOP") for h in hits), hits


def rule_b(widget, top) -> tuple[bool, list[str]]:
    """Is the widget a button that invoked, or a Text where Enter is content?"""
    tags = {str(t) for t in widget.bindtags()}
    if "TButton" in tags:
        return True, ["TButton"]
    hit = tags & CONSUMES_ENTER
    return bool(hit), sorted(hit)


def find_text(widget):
    """The `Text` descendant a key would actually be delivered to."""
    if widget.winfo_class() == "Text":
        return widget
    for child in widget.winfo_children():
        found = find_text(child)
        if found is not None:
            return found
    return None


app = bs.App(title="probe_441")
root = app._tk_root
root.geometry("460x340+120+120")
root.deiconify()
root.update()

top = tkinter.Toplevel(root)
top.geometry("460x340+160+160")
top.deiconify()
top.bind("<Return>", lambda e: None)   # the dialog's own binding

from bootstack.widgets._impl.primitives.button import Button as _Button

button = _Button(top, text="OK")
button.pack()
field = bs.TextField(parent=top)
area = bs.TextArea(parent=top, height=3)
root.update()

field_inner = getattr(field._internal, "entry_widget", field._internal)
area_inner = find_text(area._internal)
assert area_inner is not None, "precondition: found the TextArea's Text widget"

cases = [
    ("bootstack Button", button, True,
     "invokes on Return - the case the guard already handles"),
    ("TextArea's Text", area_inner, True,
     "inserts a newline - this IS #441"),
    ("TextField entry", field_inner, False,
     "the CONTROL: Enter must keep submitting, or ask_string breaks"),
]

print("MEASURED - two candidate rules over the same widgets\n")
for label, widget, expected, why in cases:
    a_says, a_hits = rule_a(widget, top)
    b_says, b_hits = rule_b(widget, top)
    print(f"  {label:<18} class={widget.winfo_class()}")
    print(f"  {'':<18} expected {expected} - {why}")
    print(f"  {'':<18} RULE A -> {a_says!s:<5} {'ok' if a_says is expected else 'FAIL'}"
          f"   via {a_hits or '(nothing)'}")
    print(f"  {'':<18} RULE B -> {b_says!s:<5} {'ok' if b_says is expected else 'FAIL'}"
          f"   via {b_hits or '(nothing)'}")
    print()
    if a_says is not expected:
        failures.append(f"RULE A misclassifies {label}: got {a_says} ({a_hits})")
    if b_says is not expected:
        failures.append(f"RULE B misclassifies {label}: got {b_says} ({b_hits})")

print("=" * 68)
a_failed = [f for f in failures if f.startswith("RULE A")]
b_failed = [f for f in failures if f.startswith("RULE B")]

for name, bad in (("A", a_failed), ("B", b_failed)):
    print(f"RULE {name}: {'CLEAN' if not bad else 'WRONG'}")
    for f in bad:
        print(f"   - {f}")

print()
if not b_failed and a_failed:
    print("=> Adopt RULE B. Rule A looks general but is not: bootstack's own")
    print("   TextField binds <Return> as an INSTANCE binding to emit its")
    print("   `submit` event, so 'has a real binding' is true for the very")
    print("   widget that must keep submitting. Interrogating bindings cannot")
    print("   separate binds-to-notify from binds-to-consume; only intent can,")
    print("   and the class name is where that intent is recorded.")
    sys.exit(0)
if not b_failed and not a_failed:
    print("=> Both classify cleanly here. Prefer B: it states the intent")
    print("   ('Enter is content in a Text') rather than inferring it.")
    sys.exit(0)
print("=> RULE B is wrong too. Do not implement either; measure a third.")
sys.exit(1)
