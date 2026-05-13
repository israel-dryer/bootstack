<!--
================================================================================
Widget page template — thin gateway model (decisions #21–26)
================================================================================

PURPOSE: Orient the reader and hand them off. Maximum ~40 lines.

FOUR SECTIONS ONLY:
  1. One-sentence description (above the quickstart — page intro)
  2. Quickstart — minimal runnable code + screenshot (≤ 20 lines)
  3. ## When to use — bullets + optional ### Consider a different control when...
  4. ## See also — three levels: Examples · Guides · API reference

DO NOT add catalog sections:
  ## Events, ## Add-ons, ## Validation, ## Common options, ## Reactivity,
  ## State, ## Keyboard navigation, ## Value model, ## Accent and variant,
  ## Density, ## Surface, ## Icons, ## Items and values, etc.

  That content belongs in:
    - docs/examples/   — task instructions, runnable annotated programs
    - docs/guides/     — cross-cutting conceptual explanations
    - docs/reference/  — API lookup (auto-generated from docstrings)

  If you're tempted to add a fifth section, it belongs in one of those layers.
================================================================================
-->

---
title: WidgetName
---

# WidgetName

`WidgetName` [one-sentence description of what it is].

```python
import bootstack as bs

app = bs.App()

bs.WidgetName(app, ...).pack(padx=20, pady=20)

app.mainloop()
```

<div class="app-window">
    <img src="../../assets/widgets-widgetname-quickstart.png" alt="WidgetName quickstart"/>
</div>

## When to use

Use `WidgetName` when:

- you need [primary use case]
- you want [secondary use case]

### Consider a different control when...

- condition-first lowercase clause — use [Widget](../path/widget.md)
- next condition — use [OtherWidget](../path/otherwidget.md)

## See also

**Examples:** [Example title](../../examples/topic/example.md) · [Another](../../examples/topic/other.md)  
**Guides:** [Relevant guide](../../guides/guide.md) · [Another guide](../../guides/other.md)  
**API reference:** [WidgetName](../../reference/widgets/widgetname.md)

---

<!--
================================================================================
AUTHORING NOTES
================================================================================

INTRO (description line)
  - One sentence. What the widget IS — not when to use it.
  - "When to use" content goes inside ## When to use, not the intro.
  - Format: backtick-quoted class name + verb clause.
    Good:  `TextEntry` is a form-ready text field with label, input, and message area.
    Bad:   `TextEntry` provides text input for forms when you need validation.

QUICKSTART
  - ≤ 20 lines including imports and mainloop().
  - Self-contained: must include `import bootstack as bs`, `bs.App()`, `app.mainloop()`.
  - Shows the primary use case, not exhaustive features.
  - Uses `bs.*` — never `ttk.*`.
  - Always followed by a screenshot.

SCREENSHOT
  - Path: `docs/assets/widgets-<slug>-quickstart.png`
  - Wrap in `<div class="app-window"><img .../></div>`
  - Required for the quickstart. No other screenshots on a thin page.

WHEN TO USE
  - 2–5 bullets. Each one a concrete, recognizable situation.
  - Opening stem: "Use `WidgetName` when:"
  - Don't restate the intro; give the reader a decision signal.

CONSIDER A DIFFERENT CONTROL
  - Opt-in — include only when the widget is in an overlapping family
    (SelectBox/OptionMenu/Combobox, TreeView/TableView/ListView, etc.).
  - Omit for simple, unambiguous widgets (Button, Label, Separator).
  - Format: condition-first lowercase, em-dash, linked widget name. No trailing "instead."
    Good:  - you need multi-select — use [TreeView](../data-display/treeview.md)
    Bad:   - **Multi-select needed**: use TreeView instead

SEE ALSO
  - Three levels: Examples · Guides · API reference (decision #23).
  - Not all levels will be populated while examples/ is being built — that's acceptable.
  - Examples: scenario-based links, e.g. "Login form", "Settings panel"
  - Guides: cross-cutting concept links, e.g. "Forms & Input", "Validation"
  - API reference: `../../reference/widgets/<slug>.md`
    These are rebuilt from `docs/snippets/api/<slug>.md` (gen_api.py output).
  - Separate multiple links within a level with ` · ` (space-middot-space).
  - End each level line with two trailing spaces for a <br> in the rendered output.

DOCSTRING QUALITY (the API reference is only as good as the docstrings)
  - Class docstring: one-sentence summary + one short orientation paragraph.
  - `Args:` on `__init__`: one line per parameter, formal signature reference.
  - `Attributes:`: only runtime-assigned names invisible to griffe (signal, variable).
  - No `!!! note "Events"`, no `Example:` blocks, no "See also" in docstrings.
  - Full conventions in CLAUDE.md decision #16.
================================================================================

PRE-PUBLISH CHECKLIST
  - [ ] Page is ≤ ~40 lines (four sections only, no catalog sections)
  - [ ] Intro is one sentence describing what the widget IS
  - [ ] No "when to use" content in the intro
  - [ ] Quickstart is self-contained (import + App() + mainloop())
  - [ ] Quickstart is ≤ 20 lines and uses bs.* imports
  - [ ] Screenshot exists and path resolves
  - [ ] ## When to use has 2–5 bullets
  - [ ] ### Consider a different control when... present only for overlapping families
  - [ ] ### Consider a different control when... follows canonical format (condition-first, em-dash, linked)
  - [ ] ## See also has all three levels (Examples / Guides / API reference)
  - [ ] All links point to real files (link validation is OFF — grep manually)
  - [ ] No catalog sections beyond the four above
================================================================================
-->