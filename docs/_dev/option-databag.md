# Initiative — Option data bag + the universal `selection` accessor

**Status:** SHIPPED. The bag + universal `selection` accessor merged in **PR #116**;
the reserved `icon`/`disabled` keys were wired up (with icon-only inferred from
blank text) in **PR #118** — which also flipped `ToggleGroup`'s default accent to
`'default'` and fixed the togglegroup disabled-background builder. Remaining
follow-on: extend `.selection` to ListView/DataTable/Tree (breaking rename, own PR).
**Builds on:** the field value/text/label model (`project_field_value_text_model`)
and the shared `Option` shape shipped in PRs #114/#115.

---

## Motivation

An option's dict form is meant to be the *extensible* member of
`Option = str | tuple[str, Any] | OptionDict`, but today the normalizer
**rejects** any key beyond `text`/`value`/`icon`/`disabled`. That contradicts the
framework's **data-bag principle** (Tree/DataTable/ListView records are flat
dicts that carry undisplayed fields transparently; `SqliteDataSource` rides them
in a hidden `_bs_data` JSON column). Options should follow the same principle:
an option is a flat record, and unrecognized keys ride along as carried data.

Decision (maintainer, 2026-06-11): a mistyped key in the dict form is the user's
risk to accept — the dict route is opt-in. So **drop the strict rejection** and
carry the extras.

## Two parts

### 1. Carry the bag (this is the foundation — option family only)

- `normalize_option` stops rejecting unknown dict keys. The normalized record is
  the **full flat dict**: `{"text", "value", ...everything else}`. `text` is still
  required; `value` still defaults to `text`.
- The recognized keys that *do* something stay `text` (display), `value`
  (emitted), and the future-reserved `icon`/`disabled` (rendering/behavior, not
  yet wired). Every other key is inert carried data.

### 2. The `selection` accessor (universal, polymorphic)

One neutral-noun property on every selection widget that returns the selected
**record(s)** — the bag, indexed by key like any other record:

```python
radio.value      # "m"                                   (the value)
radio.text       # "Medium"                              (the label)
radio.selection  # {"text":"Medium","value":"m", ...}    (the record / bag) or None

tools.value      # {"b", "i"}                            (multi: set of values)
tools.selection  # [ {...}, {...} ]                      (multi: list of records)
```

- **Polymorphic by cardinality** (matches the house idiom — `value`/`text` are
  already `str | set[str]` on ToggleGroup): single-select -> `dict | None`;
  multi-select -> `list[dict]` (empty list when none). Multi is a **list** not a
  set (records are unhashable dicts, unlike `value`'s `set[str]`).
- **Neutral noun on purpose** — "the selection" reads correctly whether one or
  many, unlike `selected_item`/`selected_items`. Chosen over a singular/plural
  pair because the pair would follow a *different* convention than the
  `value`/`text` next to it.

## Scope — which widgets get `.selection`

Seven widgets. The bag arrives two ways:

| widget | `.selection` returns | bag source |
|---|---|---|
| Select, SelectButton, RadioGroup, ToggleGroup | record dict, indexed directly | **gained here** (carry extras) |
| ListView, DataTable | record dict, indexed directly | already native (rows are dicts) |
| Tree | `TreeNode \| list[TreeNode]` | one level in — `node.data` is the dict |

Tree is the principled exception: a node carries structure (children/expand), so
`selection` returns the node handle and the bag is at `node.data`.

OUT (no records, so no bag): Calendar (`value` is a date), Checkbox/Switch/
ToggleButton (boolean), MenuButton/ContextMenu (action items, no persistent
selection), Tabs/SideNav/PageStack (navigation).

## This branch vs follow-up

- **This branch (foundation):** parts 1+2 for the **option family only**
  (Select, SelectButton, RadioGroup, ToggleGroup). The four already expose
  `value`/`text`; add `selection` returning the full record.
- **Follow-up PR (naming alignment):** add `.selection` to ListView/DataTable/
  Tree, mapping/replacing their existing `get_selected()` / `selected_rows` /
  `selected_nodes`. Separate because it renames shipped API.

## Work surface (option family)

1. **`widgets/_core/options.py`** — drop the unknown-key `ValueError` in
   `normalize_option`; `extras` already captures all non-text/value keys, so the
   record carries the full bag. `record_to_dict` already flattens to
   `{"text","value",**extras}` — that IS the `selection` payload for one option.
2. **SelectBox / OptionMenu** — both keep `_records`. Add a way to get the
   selected record(s): map current value -> record -> `record_to_dict`.
3. **RadioGroup / ToggleGroup** — they currently normalize then *discard* the
   records (only `add(text, value)` reaches the internal). To carry the bag they
   must **keep the records** (a value -> record map in the wrapper, kept in sync
   with `add()`/`remove()`), or thread extras through the internal `add`. Wrapper
   map is simpler and self-contained.
4. **Public `.selection`** on each of the four — polymorphic per cardinality
   (ToggleGroup mirrors its mode like `value` does).
5. **Tests** — `selection` returns the bag for all three input forms; extras
   carried; single vs multi shape; unknown keys no longer raise.
6. **Docs** — selection guide + the `OptionDict` note (extras now carried, not
   rejected); `Option`/`OptionDict` docstrings.

## Verify
- `python -m pytest tests/test_public_surface.py tests/widgets/public/test_select_options.py -q`
- Clean `-W` docs build; run the select/group examples.

## Deferred / future
- ✅ DONE (PR #118) — `icon` rendered beside each option, per-item `disabled`,
  and icon-only inferred from blank text. `option_display` / `option_is_icon_only`
  in `widgets/_core/options.py`; `SelectionGroupMixin._option_render`; both
  ContextMenu radiobutton backends extended.
- **Extend `.selection` to ListView/DataTable/Tree** — they already carry records
  but under divergent names (`get_selected()`/`selected_rows`/`selected_nodes`).
  Breaking rename; own PR. (The current "Next up" front-runner.)
- **Select grouping** (optgroup-style) — see `project_select_grouping`; discuss
  before building.
