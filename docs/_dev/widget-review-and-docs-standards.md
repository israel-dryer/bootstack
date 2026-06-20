# Widget Review & Docs Standards

The consolidated checklist for **reviewing a widget** (or a widget feature) and
the **standards for its documentation**. Read this before a widget review or any
widget-docs work. It gathers rules that are otherwise scattered across
`CLAUDE.md`, the per-widget doc pattern, and session-to-session feedback, plus
the conventions surfaced by the Slider/RangeSlider review (PRs #212/#213) that
this document is modeled on.

This is the *what and the standard*. The mechanical per-widget doc recipe
(file layout, screenshot commands) still lives under `CLAUDE.md` →
"Widget documentation pattern" and "API Reference & Guide page pattern"; this
brief points at it rather than repeating it.

---

## Part 1 — Reviewing a widget

A "review" is **audit → fix → test → document → file follow-ups**. Not just a
read-through.

### 1. Audit (public wrapper vs `_impl`)

Compare the public wrapper surface against the internal composite. An `Explore`
agent is a good fit. Look for two things:

- **Correctness bugs** — behavior that violates the widget's own contract.
- **Unexposed capability / API gaps** — internal features the public layer never
  surfaces, or surfaces inconsistently.

### 2. Fix correctness bugs

Recurring bug classes (all four were live in the Slider review — treat them as a
checklist for any value/interactive widget):

- **Value clamping.** Every setter and programmatic write must clamp to the
  declared range. Tightening the range (e.g. lowering `max`) must **re-clamp the
  current value**, not leave it out of bounds. A bare signal/var write that skips
  the clamping setter is a bug.
- **Disabled state.** *Every* input path must honor `disabled` — mouse, drag,
  **and every key** (it's easy to guard the arrows and forget Home/End). An
  inconsistent guard is the tell.
- **Event consistency.** Equivalent gestures fire equivalent events. If a
  drag-release emits `<<Commit>>`, a keyboard jump-to-extreme should too.
- **Keyboard traps.** A widget must not `"break"` on `<Tab>` such that focus can
  never leave it (accessibility). Switch sub-targets with a non-Tab gesture.

### 3. API hygiene (the homing checklist)

When you touch a widget, clean its public API:

- Typed params: `AccentToken`, the widget's own per-widget `variant` Literal,
  `WidgetDensity`; no low-level color kwargs; the catch-all is `**kwargs`
  (layout-only, routed through `_split_layout_kwargs`).
- **`on_*` payload audit.** A *data* event gets its specific `bootstack.events`
  payload type in the `@overload` + impl signature; a *native* event
  (`click`/`hover`/`focus`/`blur`/`resize`) keeps `Event`. Payloads render in the
  autodoc "Overloads" block, so typing the source is enough.
- Drop dead/redundant kwargs; **demote set-once config to construction-only** — a
  property is "live" only if changing it has a complete, bindable effect.
- De-Tkinter any leaks (no raw `tk.*` in the public surface or docs).

### 4. Tests

- Pure value behavior (clamp, snap, range math) is testable headlessly — Tk
  variable traces fire synchronously on `set`, so no event loop is needed; just a
  module-scoped `App` fixture.
- Event **delivery** needs a *mapped* window (`deiconify` + pump) and is
  `@pytest.mark.gui`.
- **Run GUI test files one per process** — multiple module-scoped `App` fixtures
  in one process hit the one-App-per-process crash (issue #150). Run/verify each
  file separately.
- Always run `tests/test_public_surface.py` after API changes.

### 5. Docs review (while the context is fresh)

Do the widget's doc pass in the same session — see Part 2. The behavior is fresh,
so gaps (missing Events/Keyboard sections, undocumented adjacent options) are
obvious.

### 6. File follow-ups as tracked issues

**Do not scope-creep the review branch.** Additive features and out-of-scope bugs
become GitHub issues, not commits on the review branch. The Slider review filed
#210 (a `step=` feature) and #211 (the Tab focus-trap) rather than bundling them.
Cross-link the issue back to the review in its body.

### Review verification checklist

- [ ] Bug fixes have focused tests; all pass (GUI files run per-file)
- [ ] `tests/test_public_surface.py` green
- [ ] Examples run / smoke-construct without error
- [ ] Clean `-W` docs build (see Part 2)
- [ ] Follow-ups filed as issues, cross-linked
- [ ] Held for user test/approval; per-commit approval; on a `feat/*` or `fix/*`
      branch (never commit straight to `main`)

---

## Part 2 — Docs standards

**Philosophy: the Guide carries the teaching; the API Reference is a last
resort.** A user should be able to build real things from the Guide alone.

### Lead with the mental model

Open the page with the foundational concept — how to *think about* the widget —
before any options or variations. Don't bury the mental model in a later section;
a reader who gets the model up front can follow everything after it. State what
the widget *is* and the one idea that makes it click, then build outward.

### No kitchen-sink

Don't enumerate every option and value. Teach the **decisions** a user actually
makes (e.g. "reach for `on_commit` when the work is expensive"), and let the API
Reference hold the exhaustive surface. A wall of every-kwarg prose is the
anti-pattern.

**One idea per paragraph — keep it scannable.** Short paragraphs, each making a
single point, beat a dense block. A reader should be able to skim the headings and
first lines and find what they need.

### Annotations for adjacent topics

When a section about topic A must mention an **adjacent-but-distinct** topic B,
pull that mention into a `.. note::` placed near the relevant content (e.g. right
below the section's screenshot) instead of weaving it into the main prose.

- Keep each topic its **own section** with its own heading/TOC entry — don't merge
  two topics just because they're related.
- The note flags the relationship at the exact point the reader wonders about it,
  without derailing the primary explanation.
- Link across with an RST same-page section link: `` `Section Title`_ ``
  (verify it resolves under `-W`).

Exemplars (Slider/RangeSlider): the tick-marks section ends with a note pointing
to "Snapping to steps" (`tick_step` *draws* marks vs `step` *snaps* the value);
the min/max-labels section notes that `show_minmax` is redundant when tick labels
are shown.

### Cross-reference the how-to and topic guides

A widget page is a node in a web, not an island. When a section touches a subject
that has its **own** how-to (`/tasks/*`) or topic guide (`/reference/*`), link out
to it with a `:doc:` role rather than re-teaching (or worse, half-teaching) the
subject inline — the widget page shows *this widget's* slice; the guide carries
the full model.

- **Where to link:** inline at the first mention (`:doc:`/`:ref:`), or in the
  page's **See also** list, or both. A short section on a deep subject (a widget's
  *Validation* section, a field's *Events* section) should almost always point at
  the subject's guide.
- **When it's appropriate:** the section's subject is a cross-cutting subsystem
  with a dedicated guide — validation, events, data sources, layout, theming,
  signals, localization, navigation. If the reader's natural next question is
  "how does *X* work in general?", there should be a link to X's guide right there.
- **Both directions:** the guide should also reach back to representative widgets
  (it usually does via *See also*) — but the widget→guide link is the one most
  often missing.

Motivating gap (found 2026-06-19): the form **field-items** documentation has a
*Validation* section that never `:doc:`-links the validation topic guide
(`/reference/validation`) — so a reader hits the field-level slice with no pointer
to the typed-value model, rule taxonomy, `range`, or the reactive
`field.valid`/`form.valid` surface. Fix that class of omission whenever a widget's
validation (or events/data/layout/…) section is reviewed.

### Events sections

Document the **change-vs-commit** split for interactive widgets — `on_change`
(continuous) vs `on_commit` (discrete / on release). This is a public, first-class
decision with performance stakes (a `on_change` handler runs many times a second
during a drag), **not** an implementation detail. Show a handler form and a
`Stream` form. Cross-link the payload types with `:class:`.

### Keyboard sections

Document keyboard interaction for interactive widgets — arrow keys, modifiers
(`Shift`), `Home`/`End`, and any focus-cycling. Note when a gesture also commits.

### Screenshots: one per visually-distinct usage section

Each usage section that **looks** different gets its own light+dark screenshot —
not just the hero. (The Slider review added dedicated `value` and `minmax` shots
that previously only appeared in the hero.) A *behavioral* feature that does not
render differently in a static image (e.g. step snapping) gets prose, **not** a
screenshot.

Scene workflow (full detail in `CLAUDE.md` → "Widget documentation pattern"):

- Scenes live in `docs/screenshots/<widget>.py` as a `SCENES` dict; each scene is
  a self-contained `bs.App` + `app.run()`.
- Generate: `py -3.12 docs/scripts/take_screenshots.py <widget> [--scene X]`
  (both themes by default) → `docs/_static/examples/<widget>-<scene>-{light,dark}.png`.
- Wire image directives with the `bs-screenshot-light` / `bs-screenshot-dark`
  classes.
- Keep the rst code block and its scene in sync (if a scene drops an option, drop
  it from the snippet too).

### Title casing (two-tier)

- Page H1, card titles, sidenav entries → **Title Case** (and they must all
  match — the sidenav shows the H1).
- In-page section headers → **sentence case**.
- How-to (`/tasks/*`) titles are action gerunds; Topics (`/reference/*`) keep
  noun/subsystem titles.

### Mechanics

- **Single backticks** (`default_role="code"`); keep `:class:` / `:doc:` / `:ref:`
  cross-ref roles (they're deliberate links).
- **Examples: tight, accurate, API-verified.** Keep snippets short and focused on
  the point being made; use only real param names and methods (verify against the
  public surface — no invented `.configure()`/`.cget()` or property-setter
  assignments in lambdas). **Show the relevant import on first use** so a snippet
  is copy-runnable. And **examples must run** — `python docs/examples/<widget>.py`
  (or smoke-construct) after editing.
- **Clean build, always** — incremental builds mask warnings. Build to a fresh
  temp dir and require warning-free:
  `rm -rf /tmp/bsdocs && sphinx-build -b html docs /tmp/bsdocs -W --keep-going`.
- **No toolkit internals** in docs (no `tk.*` plumbing, even to say it's hidden).
- **American English** throughout.

### Docs verification checklist

- [ ] Leads with the mental model up front (foundational concept first)
- [ ] One idea per paragraph; scannable (no kitchen-sink; Guide teaches)
- [ ] One screenshot per visually-distinct usage section (behavioral-only → prose)
- [ ] Events + Keyboard sections present for interactive widgets
- [ ] Adjacent topics are `.. note::` annotations, each topic its own section
- [ ] Sections on cross-cutting subjects (validation/events/data/layout/…) `:doc:`-link the matching how-to or topic guide
- [ ] Examples tight + API-verified, with the relevant import on first use; they run
- [ ] Title casing two-tier; H1 == card == sidenav
- [ ] Clean `-W` build; single backticks; American English

---

## Related

- `CLAUDE.md` → "Widget documentation pattern", "API Reference & Guide page
  pattern" (mechanical recipes).
- Memories: `feedback_docs_annotations_for_adjacent_topics`,
  `feedback_no_toolkit_internals_in_docs`, `feedback_run_examples`,
  `project_user_guide_fleshout`, `project_typed_event_payloads`.