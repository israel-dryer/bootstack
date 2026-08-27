"""Why does TextField.value read 'hello' after its bound signal cleared to ''?"""
import os
import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
print()

with bs.App(title="probe") as app:
    t = bs.Signal("hello", allow_empty=True)
    tf = bs.TextField(textsignal=t)
    entry = tf._entry_widget()
    print(f"   before   tf.value={tf.value!r}  entry.get()={entry.get()!r}  var={app.tk.getvar(str(t._var))!r}")
    t.clear()
    print(f"   after    tf.value={tf.value!r}  entry.get()={entry.get()!r}  var={app.tk.getvar(str(t._var))!r}")
    print(f"   entry textvariable = {entry.cget('textvariable')!r}   signal var = {str(t._var)!r}")
    print(f"   internal value attr = {tf._internal.value!r}")

    print()
    print("-- control: an ORDINARY signal set to '' (no allow_empty anywhere) --")
    u = bs.Signal("hello")
    uf = bs.TextField(textsignal=u)
    uentry = uf._entry_widget()
    u.set("")
    print(f"   after    uf.value={uf.value!r}  entry.get()={uentry.get()!r}  var={app.tk.getvar(str(u._var))!r}")
