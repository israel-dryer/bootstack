"""Probe #511 - does a shell sidebar hidden across a theme change come back stale?

The screenshot on the issue shows every region dark except the nav pane's frame
background, which stays light -- while the selected item INSIDE it repainted. So
the observable is a Tk widget's cget('background'), read per region.

One Workbench, one process, so every color is comparable (not a screen capture).

  PRECONDITION  the sidebar must be winfo_viewable() before anything is measured.
                Without it the theme walk skips the whole tree and both arms come
                out identical -- a vacuous pass. The probe aborts instead.
  baseline      sidebar visible, light theme
  ARM A         hide -> switch to dark -> show          (the reported sequence)
  ARM B         control: with the sidebar VISIBLE, switch to light and back to
                dark, reaching the SAME final theme by a path that works
  CONTROLS      the rail and content frames are visible throughout, so they say
                what a region that never missed the change looks like

A == B means no defect. A wearing the baseline color while B does not is the bug.

Run: py -3.12 development/probe_511_hidden_sidebar_theme.py
"""
from __future__ import annotations

import bootstack as bs
from bootstack.style.style import get_style


def subtree(w):
    out, stack = [], [w]
    while stack:
        cur = stack.pop()
        out.append(cur)
        try:
            stack.extend(cur.winfo_children())
        except Exception:
            pass
    return out


def backgrounds(w):
    """(path -> background) for every widget in w's subtree that reports one.

    ttk widgets raise on cget('background') -- they follow the global style and
    cannot go stale. The imperatively-painted Tk widgets are the ones at issue.
    """
    out = {}
    for cur in subtree(w):
        try:
            out[str(cur)] = str(cur.cget('background'))
        except Exception:
            continue
    return out


def pump(n=8):
    for _ in range(n):
        shell._internal.update()


def summarize(name, before, after):
    """How many widgets moved off their baseline color, and how many stayed."""
    shared = sorted(set(before) & set(after))
    moved = [k for k in shared if before[k] != after[k]]
    stayed = [k for k in shared if before[k] == after[k]]
    print(f"  {name:<10} {len(moved):>2} of {len(shared):>2} recolored, "
          f"{len(stayed):>2} still wearing the light background")
    return moved, stayed


with bs.Workbench(title="probe 511", size=(730, 550), sidebar_mode="compact",
                  undecorated=True, resizable=(False, False), collapsible=False) as shell:
    with shell.add_toolbar(show_window_controls=True) as bar:
        bar.add_theme_toggle()
    with shell.add_workspace("calendar", text="Calendar", icon="calendar3") as ws:
        with ws.page_nav() as nav:
            with nav.add_page("today", text="Today", icon="calendar-day", padding=20, gap=8):
                bs.Label("Today", font="heading-lg")
                bs.Label("No events.")
    with shell.add_workspace("settings", text="Settings", icon="gear", pin_to_footer=True) as ws:
        with ws.page_nav() as nav:
            with nav.add_page("general", text="General", icon="sliders", padding=20):
                bs.Label("Settings", font="heading-lg")

internal = shell._internal
sidebar = getattr(internal, '_sidebar', None)
rail = getattr(internal, '_rail', None)
content = getattr(internal, '_content', None)
if sidebar is None or rail is None or content is None:
    raise SystemExit("PROBE INVALID: shell slots not found; locate them before measuring")

# ---- precondition: the tree must really be on screen ------------------------
internal.winfo_toplevel().deiconify()
for _ in range(60):
    pump(2)
    if sidebar.winfo_viewable():
        break
if not sidebar.winfo_viewable():
    raise SystemExit("PROBE INVALID: sidebar never became viewable -- the theme walk "
                     "skips an unmapped tree, so both arms would agree for the wrong reason")
print(f"PRECONDITION ok: sidebar viewable = {bool(sidebar.winfo_viewable())}, "
      f"rail = {bool(rail.winfo_viewable())}, content = {bool(content.winfo_viewable())}")

bs.set_theme("bootstrap-light")
pump()
base_sidebar, base_rail, base_content = backgrounds(sidebar), backgrounds(rail), backgrounds(content)
print(f"baseline (light): sidebar {len(base_sidebar)} Tk widgets, rail {len(base_rail)}, "
      f"content {len(base_content)}")
print(f"  sample sidebar backgrounds: {sorted(set(base_sidebar.values()))[:4]}")

# ---- ARM A: the reported sequence -------------------------------------------
shell.hide_sidebar()
pump()
print(f"\nARM A  sidebar hidden: viewable = {bool(sidebar.winfo_viewable())} "
      f"(rail stays {bool(rail.winfo_viewable())})")
bs.set_theme("bootstrap-dark")
pump()
shell.show_sidebar()
pump()
print(f"ARM A  after re-show (dark): viewable = {bool(sidebar.winfo_viewable())}")
a_sidebar, a_rail, a_content = backgrounds(sidebar), backgrounds(rail), backgrounds(content)
a_moved, a_stayed = summarize("sidebar", base_sidebar, a_sidebar)
summarize("rail", base_rail, a_rail)
summarize("content", base_content, a_content)

# ---- ARM B: the control -----------------------------------------------------
bs.set_theme("bootstrap-light")
pump()
bs.set_theme("bootstrap-dark")
pump()
b_sidebar = backgrounds(sidebar)
print("\nARM B  control, toggled with the sidebar visible, same final theme:")
b_moved, b_stayed = summarize("sidebar", base_sidebar, b_sidebar)

differ = [k for k in sorted(set(a_sidebar) & set(b_sidebar)) if a_sidebar[k] != b_sidebar[k]]
print(f"\nARM A vs ARM B at the SAME theme: {len(differ)} of "
      f"{len(set(a_sidebar) & set(b_sidebar))} sidebar widgets disagree")
for path in differ[:10]:
    print(f"    {path}\n        A(hidden across change)={a_sidebar[path]}  "
          f"B(visible)={b_sidebar[path]}  baseline(light)={base_sidebar.get(path)}")

# ---- ARM D: does an EXISTING trigger recover it? -----------------------------
# PageStack._navigate already walks the subtree it shows. If switching workspace
# away and back clears the stale color, the machinery works and the only thing
# missing is a trigger on the slot re-pack -- which also gives the user a
# workaround. Re-run the reported sequence first, since ARM B repainted it.
# ARM D must re-stale in DARK, or the pane it navigates to is already the right
# color and the arm proves nothing. Show both workspaces at light first, so both
# panes are painted light, then hide, go dark, and show.
bs.set_theme("bootstrap-light")
pump()
shell.show_sidebar()
pump()
shell.navigate("settings", "general")
pump()
shell.navigate("calendar", "today")
pump()
shell.hide_sidebar()
pump()
bs.set_theme("bootstrap-dark")
pump()
shell.show_sidebar()
pump()
stale_again = backgrounds(sidebar)
print(f"\nARM D  re-staled at DARK (workspace = {shell.current_workspace}):")
for path in sorted(stale_again):
    print(f"    {stale_again[path]}  {path}")

# Prove the navigation actually happened, and that the walk it triggers is
# capable of moving a color -- otherwise "0 recolored" is a blind result.
shell.navigate("calendar", "today")
pump()
mid = backgrounds(sidebar)
print(f"  navigated to {shell.current_workspace}: "
      f"{sum(1 for k in mid if mid[k] != stale_again.get(k))} widget(s) changed color here")
for path in sorted(mid):
    print(f"    {mid[path]}  {path}")

shell.navigate("settings", "general")
pump()
after_nav = backgrounds(sidebar)
recovered = [k for k in sorted(set(stale_again) & set(after_nav))
             if stale_again[k] != after_nav[k]]
print(f"  back on {shell.current_workspace}: {len(recovered)} of {len(stale_again)} "
      f"recolored versus the stale state")
for path in sorted(after_nav):
    print(f"    {after_nav[path]}  {path}")
print("  (if NOTHING moved at either step, this arm is blind -- the navigation did"
      " not reach the sidebar's pagestack, so it says nothing about the trigger)")

# ---- diagnostic: every Tk widget, per region, in all three states -----------
# The content region is visible throughout, so anything stale THERE is a second
# finding rather than this one. Printed rather than inferred.
print("\nPER-WIDGET (light baseline -> ARM A -> ARM B)")
b_rail, b_content = backgrounds(rail), backgrounds(content)
for label, base, arm_a, arm_b in (("sidebar", base_sidebar, a_sidebar, b_sidebar),
                                  ("rail", base_rail, a_rail, b_rail),
                                  ("content", base_content, a_content, b_content)):
    for path in sorted(base):
        print(f"  {label:<8} {base[path]:>8} -> {arm_a.get(path, '?'):>8} -> "
              f"{arm_b.get(path, '?'):>8}  {path}")

print("\nREADING")
if differ:
    print("  REPRODUCED. The sidebar missed the theme change while hidden and came")
    print("  back carrying the old palette; the rail and content, visible throughout,")
    print("  recolored. ARM B reaching the same theme with different colors is what")
    print("  rules out 'dark just looks like that'.")
else:
    print("  NOT reproduced on this path. Before concluding anything, check that ARM A")
    print("  actually left the sidebar unviewable and that the baseline colors differ")
    print("  from dark at all -- an all-agreeing run is what a blind probe looks like.")

internal.winfo_toplevel().destroy()
