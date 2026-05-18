"""Visual test for TabView parity work.

Covers:
  1. tv["key"] dict-style access
  2. Typed on_tab_changed with current/previous/reason/via
  3. on_tab_activated / on_tab_deactivated
  4. hide_tab / show_tab / forget_tab
  5. keys() method
"""
import bootstack as bs

app = bs.App(title="TabView Parity — Visual Test", size=(700, 520))
log_var = bs.Signal("")

def log(msg: str) -> None:
    log_var.set(msg)
    print(msg)


# ── main layout ──────────────────────────────────────────────────────────────

outer = bs.PackFrame(app, direction="column", gap=0)
outer.pack(fill="both", expand=True)

tv = bs.TabView(outer, variant="bar")
tv.pack(fill="both", expand=True, padx=12, pady=12)

# Add four tabs
p1 = tv.add("home",     text="Home",     icon="house")
p2 = tv.add("settings", text="Settings", icon="gear")
p3 = tv.add("docs",     text="Docs",     icon="book")
p4 = tv.add("about",    text="About",    icon="info-circle")

bs.Label(p1, text="Home page content").pack(padx=20, pady=20)
bs.Label(p2, text="Settings page content").pack(padx=20, pady=20)
bs.Label(p3, text="Docs page content").pack(padx=20, pady=20)
bs.Label(p4, text="About page content").pack(padx=20, pady=20)


# ── 1. dict-style access ──────────────────────────────────────────────────────

def test_getitem():
    widget = tv["settings"]
    log(f'tv["settings"] -> {type(widget).__name__} (expect Frame)')

# ── 2. on_tab_changed typed payload ──────────────────────────────────────────

def on_changed(event):
    d = event.data
    cur  = d["current"]["key"]
    prev = d["previous"]["key"] if d["previous"] else "—"
    log(f"on_tab_changed: current={cur!r}  previous={prev!r}  reason={d['reason']}  via={d['via']}")

tv.on_tab_changed(on_changed)

# ── 3. on_tab_activated / on_tab_deactivated ─────────────────────────────────

def on_activated(event):
    print(f"  [activate]   key={event.data['key']!r}")

def on_deactivated(event):
    print(f"  [deactivate] key={event.data['key']!r}")

tv.on_tab_activated(on_activated)
tv.on_tab_deactivated(on_deactivated)


# ── control panel ─────────────────────────────────────────────────────────────

bs.Separator(outer).pack(fill="x")
ctrl = bs.PackFrame(outer, direction="column", gap=6, padding=12)
ctrl.pack(fill="x")

def section(text):
    bs.Label(ctrl, text=text, font="caption[bold]").pack(anchor="w")

def row():
    f = bs.PackFrame(ctrl, direction="row", gap=6)
    f.pack(fill="x")
    return f


section("Dict access")
r0 = row()
bs.Button(r0, text='tv["settings"]', command=test_getitem).pack(side="left")

section("keys()")
r_keys = row()
bs.Button(r_keys, text="tv.keys()", command=lambda: log(f"keys() -> {tv.keys()}")).pack(side="left")

section("hide_tab / show_tab / forget_tab")
r1 = row()
bs.Button(r1, text="hide_tab('docs')",
          command=lambda: (tv.hide_tab("docs"),   log("hide_tab('docs')"))).pack(side="left")
bs.Button(r1, text="show_tab('docs')",
          command=lambda: (tv.show_tab("docs"),   log("show_tab('docs')"))).pack(side="left")
bs.Button(r1, text="forget_tab('about')",
          command=lambda: (tv.forget_tab("about"), log("forget_tab('about') — tab gone"))).pack(side="left")

section("Programmatic select (reason=api)")
r2 = row()
for key in ("home", "settings", "docs", "about"):
    k = key
    bs.Button(r2, text=f"select({k!r})",
              command=lambda k=k: tv.select(k)).pack(side="left")

section("hide current tab (auto-selects next)")
r3 = row()
bs.Button(r3, text="hide current tab",
          command=lambda: tv.hide_tab(tv.current) if tv.current else None).pack(side="left")


# ── status bar ────────────────────────────────────────────────────────────────

bs.Separator(app).pack(fill="x")
bs.Label(app, textsignal=log_var, font="caption",
         surface="chrome").pack(fill="x", padx=12, pady=6, anchor="w")

app.mainloop()
