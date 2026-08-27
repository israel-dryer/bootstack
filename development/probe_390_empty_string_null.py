"""#390 -- would `''` serve as the empty for a realized text binding?

Q1  Does a plain (non-nullable) Signal on a TextField already round-trip the
    cleared state, without nullable= existing at all?
Q2  When a Signal is realized, is `__call__` Python-authoritative or does it read
    the var back?  That decides whether a None->'' translation can round-trip.
Q3  What does Form.clear-shaped `form.set({k: None})` do to a text field today?
"""
import os
import tkinter as tk
import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
print()

with bs.App(title="probe") as app:
    print("-- Q1: plain Signal('') on a TextField, cleared by the user --")
    sig = bs.Signal("hello")
    tf = bs.TextField(textsignal=sig)
    seen = []
    sig.subscribe(seen.append)
    tf.value = ""
    print(f"   tf.value={tf.value!r}  sig()={sig()!r}  subscribers_saw={seen!r}")
    print(f"   realized={sig._var is not None}")

    print()
    print("-- Q2: is __call__ authoritative over the var once realized? --")
    sig2 = bs.Signal("x")
    tf2 = bs.TextField(textsignal=sig2)
    print(f"   realized={sig2._var is not None}  _last={sig2._last!r}  call={sig2()!r}")
    sig2._var.set("edited-behind-the-signal")
    print(f"   after var.set(...)  _last={sig2._last!r}  call={sig2()!r}")

    print()
    print("-- Q3: form.set({k: None}) on a text editor, no signal --")
    form = bs.Form(items=[{"key": "name", "label": "Name", "editor": "text"}])
    form.set({"name": "Ada"})
    print(f"   after set Ada   get={form.get()!r}")
    form.set({"name": None})
    print(f"   after set None  get={form.get()!r}")

    print()
    print("-- Q3b: same, but the text editor carries a Signal --")
    fsig = bs.Signal("seed")
    form2 = bs.Form(
        items=[{"key": "name", "label": "Name", "editor": "text",
                 "editor_options": {"textsignal": fsig}}]
    )
    fseen = []
    fsig.subscribe(fseen.append)
    form2.set({"name": "Ada"})
    print(f"   after set Ada   get={form2.get()!r}  sig={fsig()!r}")
    form2.set({"name": None})
    print(f"   after set None  get={form2.get()!r}  sig={fsig()!r}  saw={fseen!r}")
