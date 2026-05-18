"""Visual test for the Toplevel polish RFC.

Run this script and click each button to exercise the new features.
Expected behaviour is described in each button's label.
"""
import bootstack as bs


app = bs.App(title="Toplevel Polish — Visual Test", size=(520, 540))

# ── helpers ──────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    status_var.set(msg)
    print(msg)


# ── status bar ───────────────────────────────────────────────────────────────

status_var = bs.Signal("")

# ── section builder ──────────────────────────────────────────────────────────

def section(parent, heading: str):
    bs.Label(parent, text=heading, font="body[bold]").pack(anchor="w", padx=16, pady=(12, 2))
    frame = bs.PackFrame(parent, direction="column", gap=6, padding=(16, 0, 16, 0))
    frame.pack(fill="x")
    return frame


# ═════════════════════════════════════════════════════════════════════════════
# 1. on_close= / add_close_handler / remove_close_handler
# ═════════════════════════════════════════════════════════════════════════════

f1 = section(app, "1 · Close handlers")

def test_on_close_kwarg():
    """Window closes normally; console prints the handler ran."""
    def handler():
        log("on_close= handler ran — closing")

    win = bs.Toplevel(title="on_close= kwarg", size=(300, 120),
                      center_on_screen=True, on_close=handler)
    bs.Label(win, text="Close me — handler prints to console.").pack(padx=20, pady=20)
    win.show()

def test_veto():
    """Close button is vetoed twice, then allowed."""
    count = [0]

    def handler():
        count[0] += 1
        if count[0] < 3:
            log(f"Close vetoed ({count[0]}/2) — try again")
            return False
        log("Close allowed on 3rd attempt")

    win = bs.Toplevel(title="Veto test", size=(340, 120), center_on_screen=True,
                      on_close=handler)
    bs.Label(win, text="Click × three times — first two are vetoed.").pack(padx=20, pady=20)
    win.show()

def test_add_remove():
    """add_close_handler / remove_close_handler round-trip."""
    win = bs.Toplevel(title="add / remove handler", size=(360, 160), center_on_screen=True)

    def my_handler():
        log("my_handler ran")

    def add():
        win.add_close_handler(my_handler)
        log("Handler added — close button now prints to console")

    def remove():
        win.remove_close_handler(my_handler)
        log("Handler removed — close button closes silently")

    row = bs.PackFrame(win, direction="row", gap=8, padding=20)
    row.pack()
    bs.Button(row, text="Add handler", command=add).pack(side="left")
    bs.Button(row, text="Remove handler", command=remove).pack(side="left")
    bs.Label(win, text="Close the window to test.").pack()
    win.show()

bs.Button(f1, text="on_close= kwarg — prints on close",
          command=test_on_close_kwarg).pack(fill="x")
bs.Button(f1, text="Veto — close requires 3 clicks",
          command=test_veto).pack(fill="x")
bs.Button(f1, text="add_close_handler / remove_close_handler",
          command=test_add_remove).pack(fill="x")


# ═════════════════════════════════════════════════════════════════════════════
# 2. Centering
# ═════════════════════════════════════════════════════════════════════════════

f2 = section(app, "2 · Centering")

def test_center_screen():
    win = bs.Toplevel(title="center_on_screen=True", size=(300, 120),
                      center_on_screen=True)
    bs.Label(win, text="Should appear centered on screen.").pack(padx=20, pady=20)
    win.show()

def test_center_parent():
    win = bs.Toplevel(title="center_on_parent=True", size=(300, 120),
                      transient=app, center_on_parent=True)
    bs.Label(win, text="Should appear centered over the main window.").pack(padx=20, pady=20)
    win.show()

def test_no_center():
    win = bs.Toplevel(title="No centering (WM default)", size=(300, 120))
    bs.Label(win, text="Should open at the window manager's default position.").pack(padx=20, pady=20)
    win.show()

bs.Button(f2, text="center_on_screen=True",  command=test_center_screen).pack(fill="x")
bs.Button(f2, text="center_on_parent=True",  command=test_center_parent).pack(fill="x")
bs.Button(f2, text="No centering (both False)", command=test_no_center).pack(fill="x")


# ═════════════════════════════════════════════════════════════════════════════
# 3. modal=
# ═════════════════════════════════════════════════════════════════════════════

f3 = section(app, "3 · Modal")

def test_modal_window():
    """modal='window' — main window should not be clickable while open."""
    win = bs.Toplevel(title="modal='window'", size=(340, 120),
                      modal="window", transient=app, center_on_parent=True)
    bs.Label(win, text="Try clicking the main window — it should be blocked.").pack(padx=20, pady=20)
    bs.Button(win, text="Close", command=win.destroy).pack(pady=4)
    win.show()

def test_modal_app():
    """modal='app' — entire application blocked."""
    win = bs.Toplevel(title="modal='app'", size=(340, 120),
                      modal="app", transient=app, center_on_parent=True)
    bs.Label(win, text="All app windows blocked until this closes.").pack(padx=20, pady=20)
    bs.Button(win, text="Close", command=win.destroy).pack(pady=4)
    win.show()

bs.Button(f3, text="modal='window' — blocks parent only",
          command=test_modal_window).pack(fill="x")
bs.Button(f3, text="modal='app' — blocks all windows",
          command=test_modal_app).pack(fill="x")


# ═════════════════════════════════════════════════════════════════════════════
# 4. result + block_until_closed()
# ═════════════════════════════════════════════════════════════════════════════

f4 = section(app, "4 · result + block_until_closed()")

def test_block_until_closed():
    """Shows a Yes/No dialog built from plain Toplevel; returns True/False."""
    win = bs.Toplevel(title="Confirm", size=(320, 140),
                      modal=True, transient=app,
                      center_on_parent=True,
                      resizable=(False, False))

    bs.Label(win, text="Do you agree?").pack(padx=20, pady=(20, 8))
    row = bs.PackFrame(win, direction="row", gap=8, padding=(0, 0, 0, 16))
    row.pack()

    def yes():
        win.result = True
        win.destroy()

    def no():
        win.result = False
        win.destroy()

    bs.Button(row, text="Yes", accent="success", command=yes).pack(side="left")
    bs.Button(row, text="No",  accent="danger",  command=no).pack(side="left")

    answer = win.block_until_closed()
    log(f"block_until_closed() returned: {answer!r}")

bs.Button(f4, text="Custom Yes/No dialog → result printed to console",
          command=test_block_until_closed).pack(fill="x")


# ═════════════════════════════════════════════════════════════════════════════
# Status bar
# ═════════════════════════════════════════════════════════════════════════════

bs.Separator(app).pack(fill="x", pady=(12, 0))
bs.Label(app, textsignal=status_var, font="caption",
         surface="chrome").pack(fill="x", padx=12, pady=6, anchor="w")

app.mainloop()
