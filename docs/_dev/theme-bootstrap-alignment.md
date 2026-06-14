# Theme model v2 + Bootstrap color alignment

Branch: `feat/theme-bootstrap-alignment` (off `main`).
Status: **brief / design** — model decided with the maintainer; implementation
pending.

Grew out of the AppShell styling pass (PR #136): the nav selection wash read
grayish, which traced through the subtle derivation → the semantic tokens →
the whole palette/scale model. The fix snowballed (correctly) into a simpler,
Bootstrap-aligned **theme model v2**.

---

## Why

Two problems with the current model:

1. **Grayish subtle / muted accents** — the `bootstrap-light` theme's semantic
   tokens point at `[600]` (a darkened shade), not the base `[500]`. Tinting a
   dark solid toward white desaturates → grayish subtle. (Full diagnosis below.)
2. **Massive redundancy** — 14 theme definitions (7 light/dark pairs), each
   re-declaring the *same* Bootstrap shade families (`blue:#0d6efd` etc. are
   byte-identical across themes) plus a per-mode semantic remap
   (`blue[600]` light vs `blue[400]` dark). The only real per-theme content is
   "which hue is primary" + the bg/fg tint.

v2 fixes both: define the **semantic colors directly** (as `[500]` anchors),
generate every ramp + the light AND dark variant from one definition.

---

## The v2 model

A theme **family** is defined once and generates both modes:

```python
Theme(
    name="bootstrap",
    primary="#0d6efd", success="#198754", danger="#dc3545",
    info="#0dcaf0", warning="#ffc107", secondary="#6c757d",  # [500] anchors
    light=dict(background="#ffffff", foreground="#212529"),
    dark=dict(background="#212529",  foreground="#f8f9fa"),
    # optional: neutral="#adb5bd" (gray base), per-mode accent overrides,
    # surfaces={...} pins (see Surfaces).
)
```

- **Semantic color = `[500]`** (the scale midpoint / pure brand color). Each
  anchor generates a `[100]–[900]` ramp with **Bootstrap-aligned weights** (done:
  100/200/300 = tint 80/60/40, 400 = tint 20, 600–900 = shade 20/40/60/80; our
  scale already matches Bootstrap's published values exactly).
- **Mode-aware stop selection** — the ramp is identical in both modes; only which
  stop a role uses flips:

  | role | light | dark |
  |---|---|---|
  | solid (button fill) | `[600]` | `[400]` |
  | bg-subtle (wash) | `[100]` | `[900]` |
  | border-subtle | `[200]` | `[700]` |
  | text-emphasis | `[800]` | `[300]` |

  This is why light/dark stop being one definition works: the per-mode
  `blue[600]`/`blue[400]` remap that themes do by hand today is now derived.
- **`warning`/`info`** keep a brighter solid (`[500]`) in light — they can't carry
  white text at any shade (they use dark on-color), so darkening to `[600]` only
  mutes them. Encode as a per-role stop exception (warning/info light solid =
  `[500]`).
- **Gray ramp retained** — neutrals (secondary, borders, muted text, surfaces)
  use it heavily and directly. Generated from a `neutral`/gray base; may be
  tinted with the theme hue for cohesion.
- **`secondary`** = the gray ramp's mid stop (or an explicit anchor).

### What goes away

Named accent families (`blue`/`red`/`teal`/…) are no longer addressable — you
use `primary[300]` instead of `blue[300]`. **Audit result: no code references
accent families directly** (only comments/docstring examples do). Direct family
refs also *break theme portability* (a `rose` theme has no `blue`), so removing
them is a feature. Two minor escape hatches: an optional `colors={"blue": …}`
extra-map for a one-off non-semantic accent, and a **separate** categorical
palette for data-viz (8+ distinct series — not the semantic system's job).

---

## Locked decisions (maintainer)

- **Semantic = `[500]` midpoint anchor.** ✓
- **Solid = `[600]` light / `[400]` dark** (AAA-ish, ~6.4:1; derived per mode).
  Author defines the brand color; the framework picks the accessible stop. ✓
- **Scale weights → Bootstrap** (done — 27/27 stops match). ✓
- **Subtle/border/emphasis from each semantic's own ramp**, mode-aware
  (`[100]/[200]/[800]` light, `[900]/[700]/[300]` dark). ✓ (started — currently
  via a family lookup; v2 simplifies to the semantic's own ramp.)
- **One definition per family** → both modes; per-mode accent override optional. ✓
- **Surfaces: retune values, keep token names** (no `surface=` API break). ✓

---

## Surfaces (the orthogonal piece)

The semantic simplification does **not** touch surfaces — chrome/card/raised/etc.
still derive from the background. Two issues to fix here:

1. **Tint loss on dark themes** — `tinted_surface(target_L)` rebuilds at a target
   lightness with **saturation capped at 25**, so tinted dark themes crush to
   near-neutral (ocean-dark chrome: bg `#07141f` S63 → chrome `#06080a` S25 L3).
   Fix: derive surfaces by **darkening/lightening the background** (preserves hue
   AND saturation) instead of rebuild-at-lightness.
2. **No headroom on very-dark themes** — ocean-dark bg is already L7, so there's
   no room to derive a *darker* chrome below it (even tint-preserving lands at
   L3 = black). Fix: an optional **`surfaces=` override** on `Theme` (defaults
   empty → fully derived) so such themes pin their `chrome` (a deliberate dark
   teal) — most themes still derive everything.

Plus from the alignment work (light mode): chrome `max(bg-10, 88)` = `#e6e6e6`
(L90, was L85) and softer default `stroke` (L80 → 88, ≈ Bootstrap border-color).

---

## Diagnosis (verified, kept for rationale)

- Base `shades` already ARE Bootstrap's hexes; `color_spectrum()` uses the same
  `mix(color, white|black)` primitives. The problem is `semantic = {"primary":
  "blue[600]"}` — a darkened step (`#0A52BE` L39) below the base (`#0d6efd` L52).
- Our scale now matches Bootstrap's published values exactly (after the weight
  alignment): `[100]=#cfe2ff`, `[200]=#9ec5fe`, `[800]=#052c65` — i.e. Bootstrap's
  bg-subtle / border-subtle / text-emphasis. We just weren't using them; the wash
  used an ad-hoc `mix(accent, surface, 0.08)`.
- Contrast: `[600]` is AAA (~7:1) for primary/success/danger; `[500]` is AA
  (4.5). `warning`/`info` fail white-text at every shade (dark text needed), so
  `[600]` muted them for no gain → they go `[500]`.

---

## Implementation plan

1. **`Theme` dataclass (v2 shape)** — semantic `[500]` anchors + `light`/`dark`
   blocks + optional `neutral`/`colors`/per-mode accent/`surfaces`. Keep a
   back-compat path or migrate all themes in one pass (pre-release → clean break).
2. **Generator (`theme_provider.py`)** — build per-semantic ramps from the
   anchors; gray ramp from `neutral`; **mode-aware stop selection** for
   solid/subtle/border/emphasis; the per-role `warning`/`info` stop exception.
3. **Subtle/emphasis tokens** — source from the semantic's own ramp (drop the
   family-name lookup added in the first pass).
4. **Surfaces** — tint-preserving derivation (darken/lighten bg) + `surfaces=`
   override; light chrome L90 + softer stroke (done).
5. **Themes** — collapse 14 defs → 7 families.
6. **Docstrings** — update the `blue[100]`/`orange[400]` examples in
   `theme.py`/`style.py`/`bootstyle_builder_base.py` to semantic refs.
7. **Selection default** — decide `nav_accent` default (`"primary"` vs neutral);
   the wash is now the vibrant `[100]`.

## Verification

- All 14 (→ generated) themes build; subtle/emphasis tokens resolve both modes.
- Scale still matches Bootstrap (27/27); contrast spot-check on solids.
- `pytest tests/test_public_surface.py` + theming tests; clean `-W` build.
- Visual audit across all theme families (light + dark) — the change is
  palette-wide. **Regenerate screenshots** (accent/surface-bearing pages).

## Already done on the branch (uncommitted, first pass)

- Scale weights → Bootstrap (`TINT_WEIGHTS`/`SHADE_WEIGHTS`); 27/27 match.
- `warning`/`info` → `[500]` in light themes.
- Per-semantic `*_subtle`/`*_border_subtle`/`*_emphasis` tokens (mode-aware,
  family-sourced) + `b.subtle()`/`subtle text` consume them.
- Light chrome L90 + softer stroke.
- These all fold into v2 (the generator change reshapes the *input*; the weights,
  stops, and chrome/border values carry over).
