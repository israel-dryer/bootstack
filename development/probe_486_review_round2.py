"""#486 round 2 -- the five questions round 1 did not ask.

Round 1 measured the placeholder and the write-back's granularity. This asks
about the OTHER hooks the branch adds and the states it never drove.

Arm 1  orphan     -- does a rebind release the previous <<Change>> push binding,
                     and can the branch's own test SEE it if it does not?
Arm 2  shared     -- two widgets on ONE signal. The echo guard dedupes per
                     widget, so a second widget is a new way to build a loop.
Arm 3  empty      -- a str signal declared allow_empty, then cleared.
Arm 4  destroy    -- is the core collectable once its signal outlives it (#479)?
Arm 5  readonly   -- read_only + a bound signal, both directions.

Public API only except where the question IS about an internal hook. ASCII out.
"""

import gc
import sys
import weakref

import bootstack as bs
from bootstack.widgets._impl.composites.textarea.core import _MultilineCore


def pump(app, n=6):
    for _ in range(n):
        app.tk.update()
        app.tk.update_idletasks()


def new_app(title):
    app = bs.App(title=title, size=(500, 300))
    app.__enter__()
    return app


def core_of(widget):
    inner = widget._internal
    return inner.core if hasattr(inner, "core") else inner


def bind_script(widget):
    core = core_of(widget)
    return core.text.tk.call("bind", str(core.text), "<<Change>>")


# ---------------------------------------------------------------- arm 1
def arm_orphan():
    print("-" * 74)
    print("ARM 1  orphan: does a rebind release the previous push binding?")
    print("-" * 74)
    app = new_app("p486r2-orphan")
    ta = bs.TextArea(textsignal=bs.Signal("one"))
    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)

    core = core_of(ta)
    ids = []
    for i in range(5):
        ids.append(core._signal_change_bind_id)
        core.bind_signal(bs.Signal("s%d" % i))
        pump(app)
    script = bind_script(ta)
    stale = [i for i in ids if i and i in script]
    print("  bind ids handed out : %d" % len(ids))
    print("  still in the script : %d  %s"
          % (len(stale), "*** ORPHANS ***" if stale else "OK"))

    app.tk.destroy()


# ------------------------------------------------------- arm 1, control
def arm_orphan_control():
    """Same question with the release REMOVED, so a quiet arm 1 means something.

    Runs in its own process: a second bs.App in one interpreter cannot resolve
    its ttk layouts, so the arms cannot share one.
    """
    print("-" * 74)
    print("ARM 1c orphan CONTROL: release removed from _unbind_signal")
    print("-" * 74)

    def leaky(self):
        if self._signal is not None and self._signal_trace_id is not None:
            try:
                self._signal_trace_id.cancel()
            except Exception:
                pass
        self._signal = None
        self._signal_trace_id = None
        self._signal_change_bind_id = None

    _MultilineCore._unbind_signal = leaky

    app = new_app("p486r2-orphan-control")
    first = bs.Signal("one")
    second = bs.Signal("two")
    ta = bs.TextArea(textsignal=first)
    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)
    core = core_of(ta)
    ids = [core._signal_change_bind_id]
    core.bind_signal(second)
    pump(app)
    ta.value = "after rebind"
    pump(app)
    leaked = [i for i in ids if i and i in bind_script(ta)]
    body_passes = (second() == "after rebind" and first() == "one")
    print("  orphan bindings left       : %d  %s"
          % (len(leaked), "*** ORPHANS ***" if leaked else "none"))
    print("  second() == 'after rebind' : %s" % (second() == "after rebind"))
    print("  first()  == 'one'          : %s" % (first() == "one"))
    print("  test_rebinding_leaves_the_previous_signal_alone would : %s"
          % ("STILL PASS -- VACUOUS" if body_passes else "FAIL, so it guards"))
    app.tk.destroy()


# ---------------------------------------------------------------- arm 2
def arm_shared():
    print("-" * 74)
    print("ARM 2  shared: two widgets, one signal")
    print("-" * 74)
    app = new_app("p486r2-shared")
    sig = bs.Signal("start")
    seen = []
    sig.subscribe(seen.append)
    a = bs.TextArea(textsignal=sig)
    b = bs.TextArea(textsignal=sig)
    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)
    base = len(seen)

    for i in range(5):
        a.value = "a%d" % i
        pump(app, 3)
        b.value = "b%d" % i
        pump(app, 3)
    fired = len(seen) - base
    print("  writes driven      : 10")
    print("  notifications      : %d  %s"
          % (fired, "*** RUNAWAY ***" if fired > 25 else "bounded"))
    print("  converged          : sig=%r a=%r b=%r  %s"
          % (sig(), a.value, b.value,
             "OK" if sig() == a.value == b.value else "*** DIVERGED ***"))
    app.tk.destroy()


# ---------------------------------------------------------------- arm 3
def arm_empty():
    print("-" * 74)
    print("ARM 3  empty: a str signal declared allow_empty, then cleared")
    print("-" * 74)
    app = new_app("p486r2-empty")
    try:
        sig = bs.Signal("hello", allow_empty=True)
    except TypeError as exc:
        print("  allow_empty unavailable: %s" % exc)
        app.tk.destroy()
        return
    ta = bs.TextArea(textsignal=sig)
    tfsig = bs.Signal("hello", allow_empty=True)
    tf = bs.TextField(textsignal=tfsig)
    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)
    print("  TextArea  before clear : value=%r sig=%r" % (ta.value, sig()))
    sig.clear()
    pump(app)
    print("  TextArea  after  clear : value=%r sig=%r  %s"
          % (ta.value, sig(),
             "OK" if ta.value == "" else "*** WIDGET IGNORED THE CLEAR ***"))
    tf_entry = tf._internal.entry if hasattr(tf._internal, "entry") else None
    tf_shown = (lambda: tf_entry.get() if tf_entry is not None else tf.value)
    tf_before = tf_shown()
    tfsig.clear()
    pump(app)
    print("  TextField exemplar     : shown before=%r after=%r sig=%r value=%r"
          % (tf_before, tf_shown(), tfsig(), tf.value))
    ta_shown = core_of(ta).text.get("1.0", "end-1c")
    print("  TextArea  on screen    : %r" % (ta_shown,))
    app.tk.destroy()


# ---------------------------------------------------------------- arm 4
def arm_destroy():
    print("-" * 74)
    print("ARM 4  destroy: is the widget collectable once the signal outlives it?")
    print("-" * 74)
    app = new_app("p486r2-destroy")
    sig = bs.Signal("start")
    ta = bs.TextArea(textsignal=sig)
    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)
    core = core_of(ta)
    ref = weakref.ref(core)
    comp_ref = weakref.ref(ta._internal)
    subs_before = len(getattr(sig, "_subscribers", []))
    ta._internal.destroy()          # the whole composite, not just the core:
    pump(app)                       # the composite pins the core either way
    del core, ta
    gc.collect()
    pump(app)
    subs_after = len(getattr(sig, "_subscribers", []))
    print("  subscribers before/after destroy : %d -> %d  %s"
          % (subs_before, subs_after,
             "OK" if subs_after < subs_before else "*** LEAKED ***"))
    print("  core collected                   : %s"
          % ("yes" if ref() is None else "NO -- pinned"))
    print("  composite collected              : %s"
          % ("yes" if comp_ref() is None else "NO -- pinned"))
    try:
        sig.set("after destroy")
        pump(app)
        print("  set after destroy                : no exception")
    except Exception as exc:
        print("  set after destroy                : *** %s: %s ***"
              % (type(exc).__name__, exc))
    app.tk.destroy()


# ---------------------------------------------------------------- arm 5
def arm_readonly():
    print("-" * 74)
    print("ARM 5  read_only + a bound signal")
    print("-" * 74)
    app = new_app("p486r2-readonly")
    sig = bs.Signal("locked")
    ta = bs.TextArea(textsignal=sig, read_only=True)
    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)
    print("  seeded       : value=%r sig=%r" % (ta.value, sig()))
    sig.set("from model")
    pump(app)
    print("  model write  : value=%r sig=%r  %s"
          % (ta.value, sig(),
             "OK" if ta.value == "from model" else "*** NOT APPLIED ***"))
    ta.value = "programmatic"
    pump(app)
    print("  code write   : value=%r sig=%r  %s"
          % (ta.value, sig(),
             "OK" if sig() == "programmatic" else "*** NOT PUSHED ***"))
    app.tk.destroy()


# ---------------------------------------------------------------- arm 6
def arm_writers():
    """Every PUBLIC write path, not just the two the tests drive.

    The suite covers `widget.value = ...` and a raw `text.insert`. The wrappers
    also publish insert/append/clear/undo/redo, and undo in particular does not
    obviously ride the redirector the write-back listens on.
    """
    print("-" * 74)
    print("ARM 6  public write paths: does the signal follow each one?")
    print("-" * 74)
    app = new_app("p486r2-writers")
    sig = bs.Signal("")
    ta = bs.TextArea(textsignal=sig)
    sig2 = bs.Signal("")
    ce = bs.CodeEditor(textsignal=sig2)
    app.__exit__(None, None, None)
    app.tk.deiconify()
    pump(app)

    for label, w, s in (("TextArea", ta, sig), ("CodeEditor", ce, sig2)):
        print("  %s" % label)
        w.value = "seed"
        pump(app)
        w.insert("X")
        pump(app)
        print("    insert : value=%-12r sig=%-12r %s"
              % (w.value, s(), "OK" if s() == w.value else "*** STALE ***"))
        w.append("Y")
        pump(app)
        print("    append : value=%-12r sig=%-12r %s"
              % (w.value, s(), "OK" if s() == w.value else "*** STALE ***"))
        w.undo()
        pump(app)
        print("    undo   : value=%-12r sig=%-12r %s"
              % (w.value, s(), "OK" if s() == w.value else "*** STALE ***"))
        w.redo()
        pump(app)
        print("    redo   : value=%-12r sig=%-12r %s"
              % (w.value, s(), "OK" if s() == w.value else "*** STALE ***"))
        w.clear()
        pump(app)
        print("    clear  : value=%-12r sig=%-12r %s"
              % (w.value, s(), "OK" if s() == w.value else "*** STALE ***"))
    app.tk.destroy()


ARMS = {
    "orphan": arm_orphan,
    "orphan_control": arm_orphan_control,
    "shared": arm_shared,
    "empty": arm_empty,
    "destroy": arm_destroy,
    "readonly": arm_readonly,
    "writers": arm_writers,
}

if __name__ == "__main__":
    # One arm per PROCESS. A second bs.App in the same interpreter cannot
    # resolve its ttk layouts, so sharing a process silently turns an arm into
    # a TclError rather than a measurement.
    if len(sys.argv) > 1:
        print("=" * 74)
        print("SOURCE:", bs.__file__)
        for name in sys.argv[1:]:
            ARMS[name]()
        print("=" * 74)
    else:
        import subprocess
        for name in ARMS:
            subprocess.run([sys.executable, __file__, name])
