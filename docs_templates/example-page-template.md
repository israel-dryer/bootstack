<!--
================================================================================
Example page template (decision #26)
================================================================================

PURPOSE: Show how to build a specific thing. Answers "how do I build X?"

STRUCTURE:
  1. Title — scenario-based, not widget-based ("Login form", not "TextEntry usage")
  2. One-sentence description of what the example builds
  3. Screenshot
  4. **Covers:** inline list of widgets and concepts used
  5. Complete runnable code (no ellipses — must run from a clean Python)
  6. ## Walkthrough — 3–5 annotated key decisions (not line-by-line commentary)
  7. ## See also — widgets used · guides · related examples

Examples are organized by topic/scenario under docs/examples/.
A widget may appear in multiple topic examples.
================================================================================
-->

---
title: Example title
---

# Example title

[One sentence describing what this example builds and what the user will learn.]

<div class="app-window">
    <img src="../../assets/examples-<topic>-<slug>.png" alt="[Example title] screenshot"/>
</div>

**Covers:** `WidgetA` · `WidgetB` · [concept] · [concept]

```python
import bootstack as bs

app = bs.App(title="...", size=(600, 400))

# complete, runnable example — no ellipses

app.mainloop()
```

## Walkthrough

**[Key decision or pattern]** — one or two sentences explaining why this choice
was made, what it achieves, or what to watch out for.

**[Another key decision]** — explanation. Focus on decisions that would surprise
or instruct a reader, not on restating what the code already shows.

**[Up to 3–5 total]** — keep the walkthrough tight. If a decision is obvious
from the code, skip it. If it needs more than three sentences, it belongs in a
guide instead.

## See also

**Widgets:** [WidgetA](../../widgets/path/widgeta.md) · [WidgetB](../../widgets/path/widgetb.md)  
**Guides:** [Relevant guide](../../guides/guide.md)  
**Examples:** [Related example](../topic/other.md) · [Another](../topic/other2.md)

---

<!--
================================================================================
AUTHORING NOTES
================================================================================

TITLE
  - Scenario-based: what does the user build? ("Login form", "Settings panel",
    "Data dashboard") — not widget-based ("TextEntry and Button example").
  - Sentence case, not title case.

DESCRIPTION LINE
  - One sentence. What does this example BUILD and what will the reader learn?
  - Good:  Builds a login form with email validation and a submit action.
  - Bad:   Shows how to use TextEntry and Button together.

SCREENSHOT
  - Path: `docs/assets/examples-<topic>-<slug>.png`
  - Required. Readers scan examples visually before committing to read the code.

COVERS LINE
  - Inline, on one line. Widget class names in backticks, concepts unquoted.
  - Format: `WidgetA` · `WidgetB` · validation · reactivity
  - List only what's meaningfully demonstrated — not every widget that appears.

CODE
  - Must be complete and runnable with no modifications.
  - No ellipses (`...`) — readers copy-paste and run.
  - Includes `import bootstack as bs`, `bs.App()`, `app.mainloop()`.
  - Uses `bs.*` — never `ttk.*`.
  - Aim for 30–80 lines. Under 30 may be too trivial; over 80, consider splitting.

WALKTHROUGH
  - 3–5 bullet-style entries using bold lead phrase + explanation.
  - Annotates KEY DECISIONS, not every line.
  - Ask: "Would a competent reader know why this choice was made?" If yes, skip it.
  - Good topics: non-obvious API choices, signal/validation wiring, layout strategy,
    a gotcha that's easy to get wrong.
  - Bad topics: "We create a TextEntry here" (restates code), generic advice that
    belongs in a guide.

SEE ALSO
  - Three levels: Widgets · Guides · Examples.
  - Widget links go to the thin widget page (not the API reference).
  - Separate multiple links within a level with ` · ` (space-middot-space).
  - End each level line with two trailing spaces for a <br>.
================================================================================

PRE-PUBLISH CHECKLIST
  - [ ] Title is scenario-based, not widget-based
  - [ ] Description is one sentence explaining what is built
  - [ ] Screenshot exists and path resolves
  - [ ] **Covers:** lists only meaningfully-demonstrated widgets/concepts
  - [ ] Code is complete and runnable (no ellipses, no missing imports)
  - [ ] Code uses bs.* imports
  - [ ] Code is 30–80 lines
  - [ ] Walkthrough has 3–5 entries, each annotating a key decision
  - [ ] Walkthrough entries do not restate what the code already shows
  - [ ] ## See also has Widgets · Guides · Examples levels populated
  - [ ] All links point to real files (link validation is OFF — grep manually)
================================================================================
-->