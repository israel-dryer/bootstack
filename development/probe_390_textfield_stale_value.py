"""Is TextField.value stale after ANY signal write, or only an empty one?

Pre-existing either way (the control below runs on an ordinary Signal), but the
answer decides whether it sits in #390's neighbourhood or well outside it.
"""
import os
import bootstack as bs

print("provenance:", os.path.dirname(bs.__file__))
print("branch:", os.popen("git branch --show-current").read().strip())
print()

with bs.App(title="probe") as app:
    for label, writes in (("ordinary Signal", ["world", "", "again"]),):
        sig = bs.Signal("hello")
        tf = bs.TextField(textsignal=sig)
        entry = tf._entry_widget()
        print(f"-- {label} --")
        print(f"   seed          tf.value={tf.value!r:10} entry={entry.get()!r:10} var={app.tk.getvar(str(sig._var))!r}")
        for w in writes:
            sig.set(w)
            print(f"   set({w!r:9}) tf.value={tf.value!r:10} entry={entry.get()!r:10} var={app.tk.getvar(str(sig._var))!r}")

    print()
    print("-- and does a commit resync it? --")
    entry.event_generate("<FocusOut>")
    app.tk.call("update")
    print(f"   after FocusOut tf.value={tf.value!r} entry={entry.get()!r}")
