# CLI Implementation Plan

Six phases, ordered by dependency and impact. Phases 1A-1D can be done in parallel. Phase 2 is the core feature. Phases 3-6 build on top.

---

## Phase 1 — Quick Wins (independent, no structural changes)

### 1A. Add `--theme` flag to `ttkb start`

**Files:**
- `cli/start.py` — Add `--theme` argument (default `"cosmo"`), pass to `create_project()`
- `cli/templates/__init__.py` — Add `theme` param to `create_project()`, replace hardcoded `"cosmo"` in `MAIN_PY_TEMPLATE` with `{theme}` placeholder
- `cli/config.py` — Update `generate_config()` / `write_config()` to accept `theme` param, inject into `DEFAULT_CONFIG_TEMPLATE` instead of hardcoding

### 1B. Add `ttkb list themes`

**Files:**
- `cli/__init__.py` — Register new `list` subcommand
- New file: `cli/list_cmd.py` — Handler that instantiates a hidden Tk root, calls `ThemeProvider.list_themes()`, prints formatted table, destroys root

**Decision needed:** `list_themes()` requires a Tk root. A hidden root is the pragmatic path. This won't work in headless/SSH sessions — document that requirement.

### 1C. Fix `ttkb run` to respect theme from `ttkb.toml`

**Files:**
- `cli/run.py` — After loading config, set `TTKB_THEME` env var before spawning subprocess
- `cli/templates/__init__.py` — Update `MAIN_PY_TEMPLATE` to read `os.environ.get("TTKB_THEME", "{theme}")` as fallback

### 1D. Fix PO file hardcoded date

**Files:**
- `cli/add.py` — In `_get_po_template()`, replace `2024-01-01` with `datetime.datetime.now()` formatted as `YYYY-MM-DD HH:MM+0000`

---

## Phase 2 — Template System & AppShell Support (core feature)

### 2A. Add `template` field to config schema

**Files:**
- `cli/config.py`:
  - Add `template: str = "basic"` to `AppConfig`
  - Update `from_dict()` to read `app.template` (default `"basic"` for backwards compat)
  - Update `DEFAULT_CONFIG_TEMPLATE` to include `template = "{template}"`
  - Update `generate_config()` / `write_config()` to accept `template` param

### 2B. Add `--template` flag and appshell templates

**Files:**
- `cli/start.py`:
  - Add `--template` argument, choices `["basic", "appshell"]`, default `"basic"`
  - Pass `template` through to `create_project()`
  - Warn (don't error) if `--container` is used with `--template appshell`
  - Update success message: show page-based next steps for appshell

- `cli/templates/__init__.py` — Add new template constants and update `create_project()`:

**New templates:**

`APPSHELL_MAIN_PY_TEMPLATE`:
```python
import bootstack as bs
from {module_name}.pages.home_page import HomePage
from {module_name}.pages.settings_page import SettingsPage

def main() -> None:
    shell = bs.AppShell(
        title="{app_name}",
        theme="{theme}",
        size=(1000, 650),
    )
    shell.toolbar.add_button(icon='sun', command=bs.toggle_theme)

    home = shell.add_page('home', text='Home', icon='house')
    HomePage(home)

    shell.add_separator()

    settings = shell.add_page('settings', text='Settings', icon='gear', is_footer=True)
    SettingsPage(settings)

    shell.navigate('home')
    shell.mainloop()
```

`APPSHELL_PAGE_TEMPLATE` (generic, for `ttkb add page`):
```python
import bootstack as bs

class {class_name}:
    def __init__(self, parent):
        self.parent = parent
        self._build()

    def _build(self):
        bs.Label(
            self.parent, text="{page_title}", font="heading-xl"
        ).pack(anchor="w", padx=20, pady=(20, 10))

        content = bs.LabelFrame(self.parent, text="Content", padding=20)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Add your widgets to content here
```

`HOME_PAGE_TEMPLATE` and `SETTINGS_PAGE_TEMPLATE` — starter pages with minimal but useful content.

**Updated `create_project()` logic:**
- When `template="basic"` — existing behavior (creates `views/` with GridFrame/PackFrame)
- When `template="appshell"` — creates `pages/` dir, writes `home_page.py` and `settings_page.py`, writes appshell `main.py`

**Design note:** AppShell pages are NOT subclasses of a special widget — `shell.add_page()` returns a plain frame. The page class receives that frame and populates it. This is different from the view pattern where views ARE the frame. Generated code comments should make this clear.

### 2C. Update README template for appshell

**Files:**
- `cli/templates/__init__.py` — Add `APPSHELL_README_TEMPLATE` showing the pages-based project structure:

```
{project_dir}/
├── src/{module_name}/
│   ├── __init__.py
│   ├── main.py
│   └── pages/
│       ├── __init__.py
│       ├── home_page.py
│       └── settings_page.py
├── assets/
├── ttkb.toml
└── README.md
```

---

## Phase 3 — `ttkb add page` Command

**Depends on:** Phase 2 (needs `template` field in config and page template)

**Files:**
- `cli/add.py`:
  - Add `page` sub-subcommand (alongside `view`, `dialog`, `theme`, `i18n`)
  - Arguments: `class_name` (CamelCase, e.g. `ProfilePage`)
  - Handler `run_add_page()`:
    - Load config, check `config.app.template == "appshell"` — error if not
    - Target directory: `src/<module>/pages/`
    - Call `create_page()` from templates
    - Ensure `pages/__init__.py` exists
- `cli/templates/__init__.py`:
  - Add `create_page()` function using `APPSHELL_PAGE_TEMPLATE`

---

## Phase 4 — Demo Enhancement

**Independent** (but nicer after Phase 2)

**Files:**
- `cli/demo.py` — Add `run_appshell_demo()` that launches a simplified AppShell demo (can inline from `examples/appshell_demo.py`)
- `cli/__init__.py` — Add `--appshell` flag to the `demo` subparser, route accordingly

---

## Phase 5 — `ttkb doctor` Command

**Independent**

**Files:**
- New file: `cli/doctor.py`:
  - `run_doctor()` performs validation:
    1. Find and parse `ttkb.toml`
    2. Verify `app.entry` file exists
    3. Check directory structure matches template type (`views/` for basic, `pages/` for appshell)
    4. If `[build]` section exists, check spec file exists
    5. Print summary with pass/fail indicators
- `cli/__init__.py` — Register `doctor` command

---

## Phase 6 — Theme JSON Schema Verification

**Independent** (complements Phase 5)

**Files:**
- `cli/add.py` — After writing theme JSON in `run_add_theme()`, validate required keys (`name`, `type`, `colors` with expected color keys). Simple dict check, no external library.

---

## Dependency Graph

```
Phase 1A ─┐
Phase 1B ─┤  (all parallel)
Phase 1C ─┤
Phase 1D ─┘
              ↓
Phase 2A → 2B → 2C  (sequential)
              ↓
Phase 3  (depends on Phase 2)

Phase 4  (independent)
Phase 5  (independent)
Phase 6  (independent)
```

## Risks & Decisions

| Item | Risk | Mitigation |
|------|------|------------|
| `ttkb list themes` needs Tk root | Won't work headless/SSH | Document requirement; print clear error |
| `--container` + `--template appshell` conflict | User confusion | Warn but don't error; ignore `--container` for appshell |
| Backwards compat of `ttkb.toml` | Existing projects lack `template` field | Default to `"basic"` when missing |
| Page template pattern differs from view pattern | Pages are NOT frame subclasses | Add clear comments in generated code |
| `TTKB_THEME` env var approach for `ttkb run` | Generated code must opt in | Template already generates the env check |
