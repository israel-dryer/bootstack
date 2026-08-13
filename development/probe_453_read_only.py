"""Probe: is Select.read_only distinct from allow_custom_values=False?  (#453)

This prints state; it asserts nothing, so it cannot report a stale failure.
Arm 7 (`disabled`) is the CONTROL: it proves the probe can detect a blocked
popup, without which every `popup opens = True` above it would be unreadable.

MEASURED PRE-FIX, so the post-fix run means something:

    ARM 1  plain Select()                  .read_only=True   popup opens=True
    ARM 2  Select(read_only=True)          .read_only=True   popup opens=True
    ARM 3  Select(searchable=True)         .read_only=False
    ARM 4  Select(allow_custom_values=True) .read_only=False
    ARM 5  plain, then .read_only=False    -> becomes keyboard-editable
    ARM 6  Select(searchable, read_only)   .read_only=False  popup opens=True
    ARM 7  Select(disabled=True)  CONTROL  popup opens=False

i.e. read_only never blocked the popup, a plain Select claimed to BE read-only,
and asking for read_only alongside a typing mode discarded it outright.

POST-FIX every arm inverts except 1, 3, 4 and the control: read_only blocks the
popup, survives the typing modes, and a plain Select reports False.

ASCII output only (cp1252 console).

Arms:
  1. plain Select                      -> what does .read_only report?
  2. Select(read_only=True)            -> does the popup still open?
  3. Select(searchable=True)           -> .read_only?
  4. Select(allow_custom_values=True)  -> .read_only?
  5. plain Select, .read_only = False  -> does the entry become typeable?
  6. searchable Select, .read_only=True-> does the popup open? is it typeable?
  7. control: disabled=True            -> does the popup open? (must be NO)
"""
import bootstack as bs

OPTS = ["Alpha", "Beta", "Gamma"]


def entry_state(sel):
    e = sel._entry_widget()
    return "readonly=%s disabled=%s cget=%s" % (
        e.instate(["readonly"]), e.instate(["disabled"]), e.cget("state"))


def popup_opens(sel):
    """Return True if a popup toplevel actually came up."""
    inner = sel._internal
    inner._popup_open = False
    try:
        inner._show_selection_options()
    except Exception as exc:  # pragma: no cover - diagnostic
        return "RAISED %s" % type(exc).__name__
    opened = bool(inner._popup_open)
    if opened:
        try:
            inner._close_popup(inner._popup_frame.winfo_toplevel(), inner._popup_state)
        except Exception:
            inner._popup_open = False
    return opened


def typeable(sel):
    """Can a keystroke reach the entry? readonly ttk entries refuse insert."""
    e = sel._entry_widget()
    before = e.get()
    try:
        e.insert(0, "X")
    except Exception as exc:
        return "RAISED %s" % type(exc).__name__
    after = e.get()
    if after != before:
        e.delete(0, len(after) - len(before))
    # A ttk entry in the 'readonly' STATE still accepts programmatic insert;
    # what it refuses is keyboard input. Report the state instead.
    return not e.instate(["readonly"])


with bs.App(title="probe") as app:
    plain = bs.Select(OPTS)
    ro = bs.Select(OPTS, read_only=True)
    search = bs.Select(OPTS, searchable=True)
    custom = bs.Select(OPTS, allow_custom_values=True)
    flipped = bs.Select(OPTS)
    search_ro = bs.Select(OPTS, searchable=True, read_only=True)
    dis = bs.Select(OPTS, disabled=True)

app.tk.update_idletasks()
app.tk.update()  # let after_idle click-binding install

print("ARM 1  plain Select()")
print("       .read_only      = %s   <- user never asked for read_only" % plain.read_only)
print("       entry           : %s" % entry_state(plain))
print("       popup opens     = %s" % popup_opens(plain))

print("ARM 2  Select(read_only=True)")
print("       .read_only      = %s" % ro.read_only)
print("       entry           : %s" % entry_state(ro))
print("       popup opens     = %s   <- read_only is documented to BLOCK this" % popup_opens(ro))

print("ARM 3  Select(searchable=True)")
print("       .read_only      = %s" % search.read_only)
print("       entry           : %s" % entry_state(search))

print("ARM 4  Select(allow_custom_values=True)")
print("       .read_only      = %s" % custom.read_only)
print("       entry           : %s" % entry_state(custom))

print("ARM 5  plain Select then .read_only = False")
print("       before          : %s keyboard-editable=%s" % (entry_state(flipped), typeable(flipped)))
flipped.read_only = False
print("       after           : %s keyboard-editable=%s" % (entry_state(flipped), typeable(flipped)))
print("       .read_only      = %s   <- did it become a free-text field?" % flipped.read_only)

print("ARM 6  Select(searchable=True, read_only=True)")
print("       .read_only      = %s" % search_ro.read_only)
print("       entry           : %s" % entry_state(search_ro))
print("       popup opens     = %s" % popup_opens(search_ro))

print("ARM 7  CONTROL Select(disabled=True)")
print("       .disabled       = %s" % dis.disabled)
print("       entry           : %s" % entry_state(dis))
print("       popup opens     = %s   <- control: must be False" % popup_opens(dis))

app.tk.destroy()
