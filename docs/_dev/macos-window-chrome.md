# Native macOS window chrome (follow-up initiative)

Captured 2026-06-11 (surfaced while Mac-testing the menu redesign). **Not started.**
Separate from the menu redesign — Mac-only, cross-cutting across toplevels, and
version-fragile, so it deserves its own focused spike (testable on the maintainer's Mac).

## Goal

Let macOS draw native chrome (frame, shadow, rounded corners, panel behavior) on
bootstack toplevels instead of bootstack drawing its own — so dialogs, tooltips, toasts,
and other popups feel native on Mac, without regressing Windows/Linux.

## Two threads

### 1. Don't double-draw borders on Mac

- **Decorated dialogs** (title-bar windows): the OS draws frame + shadow. If bootstack
  adds a drawn window/content border, remove it on Aqua (redundant, looks off). Audit the
  dialog impl (`bootstack/dialogs/_impl/`) for any drawn outer border.
- **Borderless popups** (Tooltip / Toast; the themed `_ToplevelContextMenu` is **Win/Linux
  only** — Mac context menus are native NSMenu, already OS-chromed, so out of scope). On
  Win/Linux we draw a 1px border so an `overrideredirect` popup has a visible edge. On Mac,
  whether to drop that border depends on thread 2 (does the popup get a *native* shadow/edge?).

### 2. `::tk::unsupported::MacWindowStyle` — native popup/utility styling

`root.tk.call("::tk::unsupported::MacWindowStyle", "style", window, <class>)` gives a
Toplevel a native macOS window class — e.g. `help` (tooltip-style), `utility`/`floating`
(palette/panel), `hud` — bringing the real system shadow, rounded corners, and panel
behavior. This is the native feel we want for Tooltip/Toast/HUD-like popups.

**Guardrails (the maintainer flagged version-dependence):**
- It lives in the **`unsupported`** namespace — available classes/attributes and behavior
  have shifted across Tk (Carbon → Cocoa) and macOS versions.
- → **Opt-in + feature-detected**: wrap in `try/except TclError`, gate on Tk version if
  needed, and **fall back to the current drawn-border approach** when unavailable. Never
  load-bearing.

## Approach (proposed)

1. A small internal helper, e.g. `apply_mac_window_style(toplevel, style)` in `_runtime/`
   that feature-detects + applies + reports success, with a no-op fallback off Aqua / when
   unsupported.
2. Tooltip / Toast: on Aqua, apply the appropriate native class and drop the drawn border;
   keep the drawn border on Win/Linux and on Aqua when the call fails.
3. Decorated dialogs: drop any redundant drawn outer border on Aqua.
4. Verify on the maintainer's Mac across at least two macOS versions if possible (the
   fragility is the whole risk).

## Out of scope

- Menus (native NSMenu already OS-chromed on Mac; the menu redesign owns those).
- Windows/Linux popup borders (keep as-is).

## Related

- Menu redesign: `docs/_dev/menu-redesign.md` (where this was surfaced).
- Window API hardening backlog (`bs.Window` escape-hatch `window_style`/`alpha`/
  `toolwindow`) — adjacent; this initiative is specifically the *native-chrome* angle.