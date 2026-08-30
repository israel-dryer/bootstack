"""#482 -- does .value follow synchronously, or only after the loop turns?

sig_test.py reads inside the button handler, immediately after set(). The probe
arms read after a root.update(). If those disagree, the fix lands one event-loop
turn later than the write, and a same-handler read still sees the old value.
"""
import os
import bootstack as bs
print("PROVENANCE", os.path.dirname(bs.__file__))

app = bs.App()
name = bs.Signal("Israel")
tf = None

def update_the_signal():
    e = tf._internal._entry
    name.set("Judy")
    print("  IMMEDIATELY after set : display=%r value=%r" % (e.get(), tf.value))
    app.tk.winfo_toplevel().update()
    print("  after one update()    : display=%r value=%r" % (e.get(), tf.value))
    print("  part._value directly  : %r" % e._value)

with app:
    tf = bs.TextField(textsignal=name)
    btn = bs.Button("Change the signal", on_click=update_the_signal)

root = app.tk.winfo_toplevel()
root.deiconify(); root.update()
root.after(50, lambda: (btn.tk.event_generate("<ButtonPress-1>", x=5, y=5),
                        btn.tk.event_generate("<ButtonRelease-1>", x=5, y=5)))
root.after(500, root.quit)
root.mainloop()
print("  FINAL after mainloop  : value=%r" % tf.value)
root.destroy()
