"""What does a `range` rule actually ACCOMPLISH on a Select?

Four scenarios, from most to least like ordinary use. Output is ASCII.
"""
import bootstack as bs

app = bs.App(title="p")
with app:
    pass

OPTS = [("One", 1), ("Seven", 7), ("Twelve", 12)]


def show(label, sel, note=""):
    ok = sel.validate()
    print("  %-46s valid=%-5s err=%-28r %s"
          % (label, ok, sel.error()[:26], note))


print("Options: [('One',1), ('Seven',7), ('Twelve',12)],  range 5..10")
print()

print("1. User picks an option that IS in the list")
for v in (1, 7, 12):
    s = bs.Select(OPTS, value=v, parent=app)
    app._tk_root.update_idletasks()
    s.add_validation_rule("range", min=5, max=10, message="pick 5..10")
    show("value=%r (an option)" % v, s)

print()
print("2. An OFF-LIST value arrives (stored record, form.set, retired option)")
for v in (3, 7, 99):
    s = bs.Select(OPTS, value=v, parent=app)
    app._tk_root.update_idletasks()
    s.add_validation_rule("range", min=5, max=10, message="pick 5..10")
    show("value=%r (not an option)" % v, s)

print()
print("3. allow_custom_values=True -- the user TYPES a value")
for typed in ("6", "99", "banana"):
    s = bs.Select(OPTS, allow_custom_values=True, parent=app)
    app._tk_root.update_idletasks()
    s.add_validation_rule("range", min=5, max=10, message="pick 5..10")
    s._internal.entry_widget.delete(0, "end")
    s._internal.entry_widget.insert(0, typed)
    show("typed %r" % typed, s, "<- 6 IS in 5..10" if typed == "6" else "")

print()
print("4. Empty")
s = bs.Select(OPTS, parent=app)
app._tk_root.update_idletasks()
s.add_validation_rule("range", min=5, max=10, message="pick 5..10")
show("nothing selected", s, "(range passes when empty, by contract)")

# ---- Is scenario 3 specific to `range`? ----
print()
print("5. The same shape with a `custom` rule doing an ordered comparison")
for typed in ("6", "banana"):
    s = bs.Select(OPTS, allow_custom_values=True, parent=app)
    app._tk_root.update_idletasks()
    s.add_validation_rule("custom", func=lambda v: v > 5, message="must exceed 5")
    s._internal.entry_widget.delete(0, "end")
    s._internal.entry_widget.insert(0, typed)
    try:
        print("  custom (v > 5), typed %-9r -> valid=%s" % (typed, s.validate()))
    except Exception as exc:
        print("  custom (v > 5), typed %-9r -> RAISED %s: %s"
              % (typed, type(exc).__name__, exc))

print()
print("READING (measured 2026-08-21, Windows box, py -3.12):")
print("  1  A `range` bound over a FIXED option list accomplishes nothing that")
print("     curating the list does not. Offering 12 and then rejecting it is")
print("     worse for the user than not offering it.")
print("  2  THE ONE REAL JOB: a Select displays an off-list value rather than")
print("     rejecting it (retired option, form.set of a stored record), and a")
print("     range bound catches an out-of-bounds one. This works today, and it")
print("     is what the branch's attach-time rejection would have broken.")
print("  3  BROKEN, and it is the mode where a bound matters most. With")
print("     allow_custom_values=True a typed '6' reports INVALID inside 5..10,")
print("     identically to '99' and to 'banana'. The typed text never decodes")
print("     to a value, so `_validation_value` falls through to the entry's raw")
print("     text and `str < int` raises TypeError, which the range branch")
print("     swallows as 'invalid'.")
print("  5  Not a `range` quirk. A `custom` rule doing the same comparison gets")
print("     a RAW TypeError instead -- out of a blur handler, into the Tk loop.")
print("     Both are PRE-EXISTING and untouched by #465.")
