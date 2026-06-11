# Initiative — Decoupled option shape for the selection family ("option data bag")

**Status:** ✅ SUPERSEDED / SHIPPED. This planning brief was realized across
PRs #114–#116 (the shared `Option` shape + text↔value decoupling + data bag +
universal `.selection`) and PR #118 (the reserved `icon`/`disabled` keys + icon-only
inference). The living record is now `docs/_dev/option-databag.md` and memory
`project_option_databag`; this file is kept only for the original design rationale.
**Sequencing (historical):** it followed the API-reference typing sweep's Data
Display batch.

---

## Motivation

`Select` and `SelectButton` are the only selection widgets where the **display
text and the stored value cannot diverge** — `options: list[str]` means
`value == text`. Meanwhile:

- `RadioGroup` / `ToggleGroup` already decouple them via
  `list[str | tuple[str, Any]]`, e.g. `[("Small", "s"), …]`.
- The project has a **data-bag philosophy** (the unified data bag carries
  undisplayed/non-scalar fields across Tree/DataTable/ListView).

So decoupled options are an established idea here; `Select` is the holdout. The
goal: let an option carry a value distinct from its label, in a shape that can
**grow** to carry per-option extras (`icon`, `disabled`, `subtitle`, …) — the
"data bag" the maintainer is gesturing at — **without** adding a fourth options
dialect to the family.

## Guiding principle

**One shared option shape across the whole selection family**, with the dict as
the extensible member. Define it once, normalize it once, consume it everywhere
(`Select`, `SelectButton`, `RadioGroup`, `ToggleGroup`).

---

## The shape (proposed)

```python
# widgets/types.py
class OptionDict(TypedDict, total=False):
    text: Required[str]      # display label (REQUIRED)
    value: Any               # stored/emitted value; defaults to `text` if omitted
    icon: str                # FUTURE — per-option icon
    disabled: bool           # FUTURE — non-selectable row
    # …open for further per-option extras (the "data bag")

Option = str | tuple[str, Any] | OptionDict
```

Accepted forms, all normalized to `(text, value, extras)`:

| Form | text | value |
|------|------|-------|
| `"Small"` | `"Small"` | `"Small"` |
| `("Small", "s")` | `"Small"` | `"s"` |
| `{"text": "Small", "value": "s"}` | `"Small"` | `"s"` |
| `{"text": "Small"}` | `"Small"` | `"Small"` (value defaults to text) |

A single helper normalizes any `Option` (and a `list[Option]`) to a canonical
internal record, so every widget shares identical coercion + validation:

```python
def normalize_option(opt: Option) -> tuple[str, Any, dict]:
    # str -> (s, s, {})
    # (text, value) -> (text, value, {})
    # {"text": ..., "value"?: ..., **extras} -> (text, value|text, extras)
    # raise a clear error on: dict missing "text"; bad tuple arity; wrong type
```

**Validation:** a dict option MUST have `text`; `value` is optional (defaults to
`text`). Raise a precise `TypeError`/`ValueError` naming the offending option —
do NOT silently accept a `{"label": …}` typo or a 3-tuple.

## Naming decision (settle once, family-wide)

The dict key is **`text`** (matches the widget display kwarg + the internal
primitives' `text=`), NOT `label`. This means re-wording the existing
RadioGroup/ToggleGroup tuple docs from "(label, value)" → "(text, value)" so the
whole family reads consistently. `value` stays `value`. (Alternative considered:
`label` — rejected; `text` aligns with `bs.Label`, `Button(text=)`, and every
primitive's `text=` kwarg.)

---

## Current state (what each widget does today)

- **`Select`** → internal `SelectBox` (`widgets/_impl/composites/selectbox.py`).
  ENTRY-backed combobox; string-only: `items: list[str]`, the field text IS the
  value (`btn._item_value = item`, `text == item`). Supports `searchable`,
  `allow_custom_values`. `Select.value` is a `str`; `Select.options` returns
  `list[str]`; has `selected_index`.
- **`SelectButton`** → internal `OptionMenu`
  (`widgets/_impl/primitives/optionmenu.py`). PURE picker backed by a ContextMenu
  of radiobutton items; `options: list[Any]` shown as text, displayed text updated
  on select. Also text==value today.
- **`RadioGroup`** / **`ToggleGroup`** → already accept `list[str | tuple[str,
  Any]]`, normalized in a small `__init__` loop (`isinstance(opt, str)` →
  `add(text=opt, value=opt)`; else `lbl, val = opt` → `add(text=lbl, value=val)`).
  These get the dict form + the shared normalizer essentially for free.

## Work surface (by component)

1. **`widgets/types.py`** — add `OptionDict` + `Option` alias + re-export from
   `bootstack.types`; add `normalize_option` (+ list helper) in a shared module
   (`widgets/_core/options.py` or similar). Add to `tests/test_public_surface.py`.
2. **`SelectBox` (the hard part)** — give it a real bidirectional **text↔value
   map** instead of treating the entry text as the value:
   - popup + field display **text**; `value`/`<<Change>>` carry **value**.
   - `selected_index`, the per-item buttons (`_item_value`), and the
     "select first filtered item on close" path all key off the normalized records.
   - search/filter matches on **text** (see edge cases below).
3. **`OptionMenu`** — easier (pure picker): store records, show text, emit value.
4. **`RadioGroup` / `ToggleGroup` wrappers** — swap their bespoke loop for the
   shared normalizer; widen the param type to `list[Option]`; re-word tuple docs.
5. **Public wrappers** — `Select(options: list[Option])`,
   `SelectButton(options: list[Option])`; `value` getter/setter operate in
   **value-space**; decide `options` property return (see below); typed
   `on_change` payload unchanged (`ChangeEvent.value` is the value).
6. **Docs + tests** — selection guide examples; round-trip tests for all three
   forms × all four widgets; the Select edge-case matrix below.

## Select-specific semantics to nail down (entry-backed)

`Select` is a text *entry*, so value≠text needs explicit rules:

- **Display:** popup rows + the entry show **text**; selecting sets the entry to
  the option's text and `value` to its value.
- **`select.value` / `<<Change>>`:** always the **value**.
- **`select.value = x` (setter):** `x` is a **value**; the widget finds the
  matching option and displays its text. Unknown value → ? (proposal: if
  `allow_custom_values`, set text to `str(x)` and value to `x`; else raise/ignore —
  DECIDE).
- **`searchable`:** filter matches on **text** (what the user sees/types).
- **`allow_custom_values=True`:** a typed string that matches no option's text has
  **value == the typed string** (no mapping exists). Document this clearly.
- **`Select.options` property:** DECIDE return shape — options-as-given,
  normalized records, or just texts. Proposal: return the **normalized records**
  (list of `{"text","value",...}`) so it round-trips; keep a `.texts`/`.values`
  convenience if useful.
- **Duplicate texts with distinct values** (or vice-versa): allowed; resolve
  selection by identity of the chosen row, not by text match. Note in docs.

## Out of scope (for the first cut)

- The FUTURE dict extras (`icon`, `disabled`, `subtitle`) — reserve the keys in
  `OptionDict` but don't implement rendering/behavior yet; land them as follow-ups
  once the text/value split ships.
- Non-string `text` (e.g. a render callback) — text is `str` for now.
- Grouped/optgroup options — separate feature.

## Verify (when built)

- `python -m pytest tests/test_public_surface.py -q` (new aliases) + a dedicated
  `tests/widgets/public/test_select_options.py` covering the three input forms,
  value/text divergence, search-on-text, custom-value mapping, and `value`
  round-trips for `Select`/`SelectButton`/`RadioGroup`/`ToggleGroup`.
- Clean `-W` docs build (selection guide gains worked examples of all three forms).
- Run `docs/examples/select.py` after wiring.

## Open questions for the maintainer (decide before coding)

1. `Select.options` property return shape (records vs given vs texts)?
2. `select.value = <unknown value>` behavior when `allow_custom_values=False`?
3. Backfill RadioGroup/ToggleGroup tuple docs "(label,value)"→"(text,value)" now,
   or keep "label" wording and only widen the type? (Recommend re-word for family
   consistency.)
