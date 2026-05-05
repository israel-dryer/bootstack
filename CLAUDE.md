# bootstack — Claude Handoff

## Project overview

bootstack is a batteries-included Python/Tkinter desktop UI framework targeting
scientific, engineering, and utility applications. It provides themed widgets,
reactive state via signals, layout containers, an AppShell navigation pattern,
and a CLI (`bootstack start`, `bootstack gallery`, etc.).

Primary working directory: `D:\Development\bootstack`
Active branch: `docs/theme-switching-clarity`

---

## Current task for this session

Generate a **single-file demo application** called `docs_scripts/demo_app.py`
that serves as a visual showcase for the bootstack homepage hero screenshot.
The app must be fully runnable with hardcoded/fake data — no backend wiring needed.

See the full prompt below.

---

## Demo app prompt

I'm building **bootstack**, a batteries-included Python/Tkinter UI framework
aimed at scientific, engineering, and utility applications. I need a single-file
demo application that showcases the framework visually — it must be **fully
runnable** with hardcoded/fake data, but nothing needs to be wired to a real
backend.

**Framework basics:**
- `bs.AppShell(title, size)` — main window with toolbar, sidebar nav, and page stack
- `shell.add_page("key", text="Label", icon="bootstrap-icon-name")` — adds a
  sidebar item and returns a Frame for content
- `bs.Button`, `bs.Label`, `bs.TextEntry`, `bs.CheckButton`, `bs.DataTable`,
  `bs.PackFrame`, `bs.GridFrame`, `bs.Card`, `bs.Badge`, `bs.Meter` etc.
- Widgets accept `accent=` ("primary", "secondary", "success", "warning",
  "danger", "info") and `variant=` ("solid", "outline", "ghost")
- `bs.Signal(value)` for reactive state
- `shell.toolbar.add_button(icon="...", command=...)` for toolbar buttons

**The app concept:** A **Data Analysis Workbench** — a scientific utility tool
for running analyses on datasets, reviewing results, and exporting reports.
Think instrument software, lab tooling, or data pipeline monitoring.

**Pages:** Add all four nav items to the sidebar so it looks populated, but
only implement content for **Analysis** and **Results**. The other pages
(`Reports`, `Settings`) can be empty frames.

**Analysis page** (main working view):
- A left panel with run parameters: a dataset dropdown, date range inputs,
  numeric threshold entries, a couple of checkboxes for options, and **Run**,
  **Stop**, **Export** buttons (use distinct accents — primary, danger, secondary)
- A right panel with a summary stats card (showing Min, Max, Mean, StdDev as
  labeled values) and a progress/status area with a meter or progress bar and a
  status badge (e.g. "Ready", "Running", "Complete")
- A data table below showing sample rows with columns: Sample ID, Timestamp,
  Channel, Value, Delta, Status — Status column uses badges (Pass/Warning/Fail)
  with appropriate accents

**Results page:**
- A toolbar row with filter controls (a text search entry, a status dropdown,
  a date input) and a Refresh button
- A large data table with 8–10 columns of realistic scientific data (IDs,
  numeric readings, units, timestamps, status badges)
- A footer row showing record count and an Export button

**Requirements:**
- All data is hardcoded — populate tables with at least 12–15 realistic rows
- Button commands can be no-ops (`lambda: None`)
- Size: `(1200, 780)`
- Use semantic accent colors meaningfully — Run=primary, Stop=danger,
  Export=secondary, Pass=success, Warning=warning, Fail=danger
- Toolbar: theme toggle (`icon="sun"`) and a settings button (`icon="gear"`)
- Aim for visual density — the app should look like a tool someone works in
  all day
- Save as `docs_scripts/demo_app.py`

---

## What to do with the output

1. Run `python docs_scripts/demo_app.py` and verify it launches
2. Fix any API mismatches (widget names, parameter names, etc.)
3. Navigate to the **Analysis** page, take a screenshot cropped to the window
   border (no OS drop shadow), save as `docs/assets/hero-demo-app.png`
4. Update `docs/index.md` to reference the new screenshot:
   change `assets/widget-gallery-hero.png` → `assets/hero-demo-app.png`
5. Commit everything to `docs/theme-switching-clarity`

---

## Key API notes for writing working code

- Import: `import bootstack as bs`
- App entry: `app = bs.AppShell(title="...", size=(w, h))` then `app.mainloop()`
- Pages: `page = shell.add_page("key", text="Label", icon="icon-name")`
- Layout: `bs.PackFrame(parent, direction="horizontal"|"vertical", gap=N, padding=N)`
- Signals: `sig = bs.Signal(value)` — widgets accept `signal=sig`
- The `DataTable` widget takes columnar data — check current API before assuming
  kwargs; look in `src/bootstack/` if uncertain
- Bootstrap Icons are used for icon names (e.g. `"house"`, `"table"`,
  `"bar-chart"`, `"gear"`, `"sun"`, `"bell"`)
