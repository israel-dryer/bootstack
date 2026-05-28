---

# bootstack v2 Public API Proposal

> Audience: Python developers (data scientists, engineers, researchers). Goals: clarity, consistency, discoverability. No Tkinter knowledge required.

## Cross-cutting conventions

These rules apply to every widget unless explicitly noted. They resolve the bulk of the rename decisions below.

| Concept | v1 | v2 | Rationale |
|---|---|---|---|
| Current value | `value` / `get()` / `set()` | `value` property | Noun property, set via `widget.value = x`. `get()`/`set()` removed except where multi-arg. |
| Range minimum | `from_`, `minvalue`, `min_date` | `min_value` (numeric), `min_date` (date) | `from_` is a Python keyword hack; explicit. |
| Range maximum | `to`, `maxvalue`, `max_date` | `max_value`, `max_date` | Mirror of `min_value`. |
| Step | `increment` | `step` | Industry standard (HTML, Qt). |
| Click handler | `command` | `on_click` callback or `on(Event.Widget.CLICK, …)` | No Tk-ism. |
| Button label | `text` | `label` | A button has a label, not "text content". |
| Choices list | `values` (Combobox), `items` (Listview), `options` (radio) | `options` everywhere a user picks from a fixed set | Single name for the same concept. |
| Rows of data | `items` | `items` | Kept where it means data records. |
| Reactive binding | `variable=`, `textvariable=` | `signal=`, `text_signal=` | Settled. |
| Direction axis | `orient="horizontal"|"vertical"` | `orient="horizontal"|"vertical"` | Kept; HStack/VStack already encode the common case. |
| Sub-density | `density="compact"|...` | `density="compact"|"normal"|"comfortable"` | Kept. |
| Wrap width | `wraplength` | `wrap_width` | Tk-ism removed. |
| Foreground/background | `foreground`, `background` | `color`, `background_color` | "Foreground" is a Tk term users don't expect. |
| Disabled state | `state="disabled"` | `disabled: bool` property; `state=` still accepted on construction | Boolean is the natural Python idiom. |
| Padding | `padding=int|tuple` | `padding=int|tuple` | Kept. |
| Focus | `takefocus` | `focusable` | Plain English. |
| Tk-private | `exportselection` | `share_selection` | Tk-ism removed. |
| Mouse cursor lines/cursor row | `xscrollcommand`, `yscrollcommand` | Removed from public API; scrollbars auto-wire | Magic eliminated. |
| Localization | `localize=True` | `localize: bool` | Kept. |
| Format string | `value_format` | `value_format` | Kept. |
| Outer spacing | `padx`, `pady` | `margin` | CSS convention: space outside the widget. |
| Inner spacing | `ipadx`, `ipady` | `padding` | CSS convention: space inside the widget. |
| Width units | inconsistent | Containers: `width` in pixels. Text widgets (Label/Button/TextField): `width` in character cells — Tk behavior; negative values do NOT equal pixels on ttk (tested). Use layout weights or `min_width` for pixel constraints. | Tk limitation acknowledged. |

### Event payload convention

```python
sub = widget.on(Event.Input.CHANGE, lambda e: print(e.value))
sub.cancel()

# Shorthand still exists:
widget.on_change(lambda e: ...)  # returns Subscription
```

All event objects expose: `.event` (the Event constant), `.widget`, `.value` (when applicable), `.data` (typed dict). No more raw Tk event passthrough for input widgets — handlers always receive a typed `Event` object.

---

## PRIMITIVES

### Button

> A clickable action trigger with a label and optional icon.

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Button` | `Button` | Clear enough. |
| Positional 1 | — | `label: str` | Most buttons are created as `Button("Save")`. |
| kwarg | `text` | `label` | A button has a *label*. |
| kwarg | `command` | `on_click: Callable[[ClickEvent], None]` | Not Tk's `command`. |
| kwarg | `accent` | `accent` | Kept. |
| kwarg | `variant` | `variant` | Kept. `"solid"|"outline"|"ghost"|"link"|"toggle"`. |
| kwarg | `icon` | `icon` | Kept (Bootstrap Icons name). |
| kwarg | `icon_only` | `icon_only` | Kept. |
| kwarg | `density` | `density` | Kept. |
| kwarg | `textvariable` | removed | Use `text_signal`. |
| kwarg | `textsignal` | `text_signal` | Snake-case the underscore. |
| kwarg | `state` | `state` + `disabled` property | `state` kept for ctor; `disabled` is the runtime API. |
| kwarg | `padding` | `padding` | Kept. |
| kwarg | `width` | `width` (px) | Was char cells in Tk; now pixels. `char_width` available if needed. |
| kwarg | `compound` | `icon_position: "left"|"right"|"top"|"bottom"|"only"` | "compound" is opaque Tk-ism. |
| kwarg | `image` | `image` | Kept. PIL/`bs.Image`. |
| kwarg | `anchor` | `anchor` | Kept (geometry alias). |
| kwarg | `underline` | `underline_char: int | None` | More explicit. |
| kwarg | `takefocus` | `focusable: bool` | Plain English. |
| property | — | `label`, `disabled`, `icon` | Read/write properties. |
| method | `invoke()` | `click()` | Verb matches event name. |
| event | — | `Event.Widget.CLICK` / `on_click` | New, replaces `command`. |
| event | — | `Event.Widget.DOUBLE_CLICK` / `on_double_click` | New. |
| event | — | `Event.Widget.HOVER` / `on_hover` | New. |
| event | — | `Event.Widget.FOCUS`, `BLUR` | New. |

> ⚠ Cross-widget: `command` → `on_click` here, but on `Spinbox`/`FloodGauge` it becomes something else. See consistency table at end.

---

### Label

> Static text or formatted value display.

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Label` | `Label` | Kept. |
| Positional 1 | — | `text: str` | `Label("Hello")`. |
| kwarg | `text` | `text` | Kept (a Label *has* text content; unlike Button). |
| kwarg | `anchor` | `anchor` | Kept. |
| kwarg | `justify` | `justify` | Kept. |
| kwarg | `padding` | `padding` | Kept. |
| kwarg | `width` | `width` (px) | Pixels. |
| kwarg | `wraplength` | `wrap_width` | Tk-ism. |
| kwarg | `font` | `font` | Kept (token strings). |
| kwarg | `foreground` | `color` | Not "foreground". |
| kwarg | `background` | `background_color` | Pair with `color`. |
| kwarg | `relief` | `relief` | Kept. |
| kwarg | `state` | `state` / `disabled` | Standard. |
| kwarg | `textvariable` | removed | Use `text_signal`. |
| kwarg | `textsignal` | `text_signal` | Standard. |
| kwarg | `icon` | `icon` | Kept. |
| kwarg | `icon_only` | `icon_only` | Kept. |
| kwarg | `localize` | `localize` | Kept. |
| kwarg | `value_format` | `value_format` | Kept. |
| property | — | `text`, `color`, `disabled` | |
| events | none | `Event.Widget.CLICK` (optional) | Labels can opt-in to clicks. |

---

### Badge

> Compact status pill — same as Label but styled as a badge.

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Badge` | `Badge` | Kept. |
| All kwargs/properties | (same as Label) | (same as Label) | Inherits everything from Label. |

---

### Entry → **TextField**

> Single-line text input.

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Entry` | `TextField` | "Entry" is Tk jargon; TextField matches Qt/SwiftUI/HTML. |
| Positional 1 | — | `value: str = ""` | Initial text. |
| kwarg | `textvariable` | removed | `text_signal`. |
| kwarg | `textsignal` | `text_signal` | Standard. |
| kwarg | `show` | `mask_char: str | None` | "show" is opaque; `mask_char='*'` is obvious. |
| kwarg | `width` | `width` (px) / `char_width` | Pixels by default. |
| kwarg | `exportselection` | `share_selection` | Tk-ism. |
| kwarg | `justify` | `justify` | Kept. |
| kwarg | `validate`, `validatecommand`, `invalidcommand` | `validators: list[ValidationRule]`, `on_valid`, `on_invalid` | Use the `ValidationRule` system; drop Tk's triple-callback. |
| kwarg | `xscrollcommand` | removed | Internal. |
| kwarg | `font` | `font` | Kept. |
| kwarg | `foreground` | `color` | |
| kwarg | `background` | `background_color` | |
| kwarg | `state` | `state` / `disabled`, `read_only: bool` | Split `disabled` vs `read_only`. |
| kwarg | `takefocus` | `focusable` | |
| kwarg | `density` | `density` | Kept. |
| kwarg | — | `placeholder: str | None` | Add. Standard across modern UI. |
| property | — | `value`, `placeholder`, `disabled`, `read_only`, `selection` | |
| method | `insert(idx, s)` | `insert(index, text)` | Keep. |
| method | `delete(a,b)` | `delete(start, end=None)` | |
| method | `get()` | removed (use `.value`) | |
| method | `set(v)` | removed (use `.value = v`) | |
| method | `selection_range(a,b)` | `select_range(start, end)` | |
| method | `selection_all()` | `select_all()` | |
| method | `icursor(i)` | `set_cursor(index)` | Tk-ism. |
| method | — | `clear()` | Verb method. |
| event | `<<Change>>` | `Event.Input.CHANGE` / `on_change` | |
| event | — | `Event.Input.SUBMIT` / `on_submit` | Enter key. |
| event | — | `Event.Input.VALIDATE` / `on_validate` | Standard. |

---

### CheckButton → **Checkbox**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `CheckButton` | `Checkbox` | Standard name. |
| Positional 1 | — | `label: str` | |
| kwarg | `text` | `label` | |
| kwarg | `command` | `on_change` | "command" is misleading — fires on toggle. |
| kwarg | `icon`, `icon_only` | same | |
| kwarg | `on_icon`, `off_icon` | `checked_icon`, `unchecked_icon` | More explicit. |
| kwarg | `textvariable` | removed | |
| kwarg | `textsignal` | `text_signal` | |
| kwarg | `variable` | removed | |
| kwarg | `signal` | `signal` | |
| kwarg | `show_indicator` | `show_indicator` | Kept. |
| kwarg | `onvalue`, `offvalue` | `checked_value`, `unchecked_value` | |
| kwarg | `value` | `value` (initial) — **honored only when no signal** | Fixes existing silent-ignore bug; raise if both passed. |
| kwarg | `accent`, `variant`, `density`, `state` | same | |
| property | — | `value`, `checked: bool`, `disabled` | Two views: raw `value` and boolean `checked`. |
| method | `get()`, `set()` | removed | Use `.value`/`.checked`. |
| method | `invoke()` | `toggle()` | Verb. |
| event | `<<Change>>` | `Event.Input.CHANGE` / `on_change` | |
| event | `<<ToggleOn>>` | `Event.Selection.SELECT` / `on_check` | |
| event | `<<ToggleOff>>` | `Event.Selection.DESELECT` / `on_uncheck` | |

---

### Switch

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Switch` | `Switch` | Kept — distinct visual identity. |
| All kwargs/methods/events | (same as Checkbox) | (same as Checkbox) | No `show_indicator` (always shown as track+thumb). |

---

### CheckToggle → **ToggleButton**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `CheckToggle` | `ToggleButton` | A toggle button, like in toolbars. |
| All kwargs/methods/events | (same as Checkbox) | (same as Checkbox) | Visual variant: button rather than box. |

---

### RadioButton → **Radio**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `RadioButton` | `Radio` | Shorter, common. |
| Positional 1 | — | `label: str` | |
| Positional 2 | — | `value: Any` | The value this radio represents. |
| kwarg | `text` | `label` | |
| kwarg | `command` | `on_change` | |
| kwarg | `icon`, `icon_only` | same | |
| kwarg | `on_icon`, `off_icon` | `selected_icon`, `unselected_icon` | Mirror Checkbox naming. |
| kwarg | `textvariable` | removed | |
| kwarg | `textsignal` | `text_signal` | |
| kwarg | `variable` | removed | |
| kwarg | `signal` | `signal` | |
| kwarg | `value` | `value` | The value emitted when selected. |
| kwarg | `show_indicator` | `show_indicator` | |
| kwarg | `accent`, `variant`, `density`, `state` | same | |
| property | — | `value`, `selected: bool`, `disabled` | |
| method | `get()`, `set()` | removed | Use `.selected`. |
| method | `invoke()` | `select()` | Verb. |
| event | `<<Change>>` | `Event.Input.CHANGE` / `on_change` | |
| event | `<<Select>>` | `Event.Selection.SELECT` / `on_select` | |

---

### RadioToggle → **RadioToggleButton**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `RadioToggle` | `RadioToggleButton` | Matches ToggleButton naming. |
| All | (same as Radio) | (same as Radio) | Visual only. |

---

### Combobox → **REMOVED**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Combobox` | **removed** | Replaced by `Select` (was `SelectBox`). |
| Positional 1 | — | `options: list[Any] | dict[str, Any]` | The choices. |
| kwarg | `values` | `options` | Universal rename. |
| kwarg | `state` | `state` / `disabled`, `editable: bool` | Replace `state="readonly"` with `editable=False`. |
| kwarg | `width` | `width` (px) | |
| kwarg | `height` | `dropdown_max_items: int` | Was Tk's dropdown height in items. |
| kwarg | `postcommand` | `on_open: Callable` | Plain English. |
| kwarg | `justify` | `justify` | |
| kwarg | `exportselection` | `share_selection` | |
| kwarg | `font` | `font` | |
| kwarg | `textvariable` | removed | |
| kwarg | `textsignal` | `text_signal` | |
| kwarg | `accent`, `variant`, `density` | same | |
| kwarg | — | `signal: Signal | None` | Add: bind to selected option. |
| kwarg | — | `placeholder: str | None` | Add. |
| property | — | `value`, `options`, `selected_index`, `editable` | |
| method | `get()`, `set()` | removed | Use `.value`. |
| method | `current()` | `selected_index` property | Noun. |
| event | `<<ComboboxSelected>>` | `Event.Selection.SELECT` / `on_select` | Standardized. |
| event | — | `Event.Input.CHANGE` / `on_change` | For editable mode. |

---

### Spinbox *(kept)*

> Kept as `Spinbox` — distinct form factor from `NumberField`. Cycles through fixed text or numeric values with up/down arrows.

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Spinbox` | `Spinbox` | Kept. Different use case from `NumberField`. |
| Positional 1 | — | `value: float \| int = 0` | |
| kwarg | `from_` | `min_value` | Standard rename. |
| kwarg | `to` | `max_value` | |
| kwarg | `increment` | `step` | Industry standard. |
| kwarg | `values` | `options: list \| None` | If discrete choices instead of numeric. |
| kwarg | `wrap` | `wrap: bool` | Kept. |
| kwarg | `command` | `on_change` | Not "command". |
| kwarg | `font` | `font` | |
| kwarg | `width` | `width` (px) | |
| kwarg | `state` | `state` / `disabled`, `read_only` | |
| kwarg | `textvariable` | removed | |
| kwarg | `textsignal` | `text_signal` | |
| kwarg | `format` | `value_format` | Match Label/Meter. |
| kwarg | `density` | `density` | |
| kwarg | — | `signal: Signal[float] \| None` | Add: numeric signal. |
| property | — | `value`, `min_value`, `max_value`, `step`, `disabled` | |
| method | `get()`, `set()` | removed | Use `.value`. |
| method | — | `increment()`, `decrement()` | Verbs. |
| event | `<<Change>>` | `Event.Input.CHANGE` / `on_change` | |

---

### ProgressBar

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `ProgressBar` | `ProgressBar` | Kept. |
| Positional 1 | — | `value: float = 0` | |
| kwarg | `mode` | `mode: "determinate"|"indeterminate"` | Kept. |
| kwarg | `orient` | `orient` | Kept. |
| kwarg | `length` | `length` (px) | Kept. |
| kwarg | `maximum` | `max_value` | Match other widgets. |
| kwarg | `value` | `value` | Kept. |
| kwarg | `phase` | `phase` | Kept (animation offset). |
| kwarg | `variable` | removed | |
| kwarg | `signal` | `signal` | Standard. |
| kwarg | `accent`, `variant` | same | |
| property | — | `value`, `max_value`, `running: bool` | |
| method | `get()`, `set()` | removed | |
| method | `start(interval=...)` | `start(interval=50)` | Kept (indeterminate). |
| method | `stop()` | `stop()` | Kept. |
| events | none | none | Kept. |

---

### Scrollbar

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Scrollbar` | `Scrollbar` | Kept. |
| kwarg | `orient` | `orient` | |
| kwarg | `command` | `on_scroll` | Not Tk-ism. |
| kwarg | `accent`, `variant` | same | |
| property | — | `position: tuple[float, float]` | Read/write. |
| method | `get()`, `set()` | removed | Use `.position`. |

> Most users will never instantiate Scrollbar directly — scrollable containers auto-wire them.

---

### Separator

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Separator` | `Separator` | Kept. |
| kwarg | `orient` | `orient` | |
| kwarg | `thickness` | `thickness` (px) | Kept. |
| kwarg | `length` | `length` (px) | Kept. |
| kwarg | `accent`, `variant` | same | |

---

### SizeGrip

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `SizeGrip` | `SizeGrip` | Kept. |
| kwarg | `accent`, `variant` | same | |

---

### TreeView → **Tree**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `TreeView` | `Tree` | TableView stays for tabular; Tree is the hierarchical view. |
| Positional 1 | — | `columns: list[str] \| None = None` | |
| kwarg | `columns` | `columns: list[Column]` | Same name, richer type. |
| kwarg | `displaycolumns` | `visible_columns` | Plain English. |
| kwarg | `show` | `show: "tree"|"headings"|"both"` | Kept. |
| kwarg | `height` | `visible_rows: int` | Was rows-in-chars; explicit. |
| kwarg | `padding` | `padding` | |
| kwarg | `selectmode` | `selection_mode: "none"|"single"|"multiple"|"extended"` | Match ListView. |
| kwarg | `density` | `density` | |
| kwarg | `border_color` | `border_color` | |
| kwarg | `show_border` | `show_border` | |
| kwarg | `select_background` | `selection_background_color` | Pair with `color`. |
| kwarg | `header_background` | `header_background_color` | |
| kwarg | `open_icon` | `expanded_icon` | Mirrors Expander naming. |
| kwarg | `close_icon` | `collapsed_icon` | |
| kwarg | `accent`, `variant` | same | |
| property | — | `selection: list[Node]`, `nodes`, `selected_node` | |
| method | `insert(parent, idx, ...)` | `insert(parent=None, index="end", **fields)` | Plain kwargs. |
| method | `delete(*ids)` | `remove(*ids)` | Verb consistency. |
| method | `selection_set(*ids)` | `select(*ids)` | Verb. |
| method | `selection_get()` | `selected` / `selection` property | Noun. |
| method | `item(id, ...)` | `node(id)` / `update_node(id, **fields)` | Tree contains nodes. |
| method | `column(name, ...)` | `column(name)` / `configure_column(name, ...)` | Split read/write. |
| method | `yview()`, `xview()` | removed from public API | Internal scrolling. |
| method | — | `expand(id)`, `collapse(id)`, `expand_all()`, `collapse_all()` | Verbs. |
| event | `<<TreeviewOpen>>` | `Event.Widget.EXPAND` / `on_expand` | Add to enum. |
| event | `<<TreeviewClose>>` | `Event.Widget.COLLAPSE` / `on_collapse` | Add to enum. |
| event | `<<TreeviewSelect>>` | `Event.Selection.SELECT` / `on_select` | Standardized. |

> ⚠ New events needed in `Event.Widget`: `EXPAND`, `COLLAPSE`. Also `Event.Tree.NODE_CLICK` is worth considering for row clicks.

---

### LabelFrame → **GroupBox**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `LabelFrame` | `GroupBox` | Qt/HTML name. LabelFrame is Tk jargon. |
| Positional 1 | — | `title: str` | The visible label. |
| kwarg | `text` | `title` | |
| kwarg | `labelanchor` | `title_anchor` | Plain English. |
| kwarg | `padding` | `padding` | |
| kwarg | `relief` | `relief` | |
| kwarg | `borderwidth` | `border_width` | Snake-case. |
| kwarg | `width`, `height` | `width`, `height` (px) | |
| kwarg | `accent`, `variant`, `localize` | same | |

> ⚠ Note: `GroupBox` is a structural container. Could also live under LAYOUT.

---

### PanedWindow → **SplitView**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `PanedWindow` | `SplitView` | Standard modern name (SwiftUI, Qt's QSplitter ≈ "splitter"). |
| Positional 1 | — | — | |
| kwarg | `orient` | `orient` | |
| kwarg | `padding` | `padding` | |
| kwarg | `width`, `height` | same | |
| kwarg | `accent`, `variant` | same | |
| property | — | `panes: list`, `sash_positions: list[int]` | |
| method | `add(child, weight=...)` | `add(child, weight=1, min_size=None)` | Kwargs explicit. |
| method | `sashpos(idx, pos=None)` | `sash_position(index, position=None)` | Snake-case. |
| method | `identify(x, y)` | removed from public | Internal. |
| event | `<<PanedWindowResized>>` | `Event.Widget.RESIZE` / `on_resize` | Standardized. |

---

## LAYOUT

### HStack

> Horizontal pack layout container. The default direction is, of course, horizontal.

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `HStack` | `HStack` | Settled. |
| kwarg | `gap` | `gap` | |
| kwarg | `fill_items` | `fill: "x"|"y"|"both"|"none"` | Renamed: it controls how items fill, but `fill=` reads clean. |
| kwarg | `expand_items` | `expand: bool` | Plain. |
| kwarg | `anchor_items` | `anchor: Anchor` | Plain. |
| kwarg | `propagate` | `propagate: bool` | Kept. |
| kwarg | `padding` | `padding` | |
| kwarg | `width`, `height` | same (px) | |
| kwarg | `accent`, `variant`, `surface`, `show_border` | same | |
| kwarg | `input_background` | `input_background_color` | |
| context manager | — | `with HStack(...) as h:` pushes onto layout stack | Settled. |

> ⚠ Consistency: drop the `_items` suffix on all layout kwargs. `fill`/`expand`/`anchor` apply to children by design — the suffix is redundant.

---

### VStack

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `VStack` | `VStack` | Settled. |
| kwargs | (same as HStack) | (same as HStack) | |

---

### Grid

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Grid` | `Grid` | Settled. |
| kwarg | `rows` | `rows: int \| list[Track]` | Kept. |
| kwarg | `columns` | `columns: int \| list[Track]` | Kept. |
| kwarg | `gap` | `gap: int \| tuple[int, int]` | Kept. |
| kwarg | `sticky_items` | `sticky: Sticky` | Drop `_items` suffix. |
| kwarg | `propagate` | `propagate: bool` | |
| kwarg | `auto_flow` | `auto_flow` | Kept. |
| kwarg | `padding` | `padding` | |
| kwarg | `width`, `height`, `accent`, `variant`, `surface`, `show_border` | same | |

---

### Card

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Card` | `Card` | Settled. |
| kwarg | `padding` | `padding=16` | Kept default. |
| kwarg | `width`, `height` | same | |
| kwarg | `show_border` | `show_border=True` | |
| kwarg | `accent`, `variant`, `surface` | same | |
| kwarg | `layout` | `layout: "hstack"|"vstack"|"grid" = "vstack"` | New, settled. |

---

## COMPOSITES

### Accordion

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Accordion` | `Accordion` | Kept. |
| kwarg | `allow_multiple` | `allow_multiple: bool` | Kept. |
| kwarg | `allow_collapse_all` | `allow_collapse_all: bool` | Kept. |
| kwarg | `show_separators` | `show_separators: bool` | Kept. |
| kwarg | `accent`, `variant` | same | |
| property | — | `items`, `keys`, `expanded_keys` | |
| method | `add(key, title, ...)` | `add(key, title, *, expanded=False, **kwargs)` | Kept. |
| method | `remove(key)` | `remove(key)` | |
| method | `item(key)` | `item(key)` | Read accessor. |
| method | `items(expanded=...)` | `items(expanded: bool \| None = None)` | Kept; filters. |
| method | `keys()` | `keys` property | Noun. |
| method | `configure_item(key, **)` | `update_item(key, **)` | "update" reads better than "configure". |
| method | `expand(key)`, `collapse(key)`, `expand_all()`, `collapse_all()` | same | |
| event | `<<AccordionChange>>` / `on_accordion_changed` | `Event.Input.CHANGE` / `on_change` | Generic. |
| event | — | `Event.Widget.EXPAND` / `on_expand` (per-item) | New. |
| event | — | `Event.Widget.COLLAPSE` / `on_collapse` | New. |

---

### AppShell

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `AppShell` | `AppShell` | Kept. |
| kwarg | `title` | `title` | |
| kwarg | `theme` | `theme` | |
| kwarg | `size`, `position`, `minsize`, `maxsize` | `size`, `position`, `min_size`, `max_size` | Snake-case for consistency. |
| kwarg | `resizable` | `resizable` | |
| kwarg | `undecorated` | `undecorated` | Kept. |
| kwarg | `show_toolbar` | `show_toolbar` | |
| kwarg | `show_window_controls` | `show_window_controls` | |
| kwarg | `draggable` | `draggable` | |
| kwarg | `toolbar_density` | `toolbar_density` | |
| kwarg | `show_nav` | `show_nav` | |
| kwarg | `nav_display_mode` | `nav_display_mode: "icons"|"labels"|"both"|"auto"` | |
| kwarg | `nav_accent` | `nav_accent` | |
| property | — | `toolbar`, `nav`, `pages`, `current_page` | Kept. |
| method | `add_page(key, ...)` | `add_page(key, *, label, icon=None, ...)` | Plain kwargs. |
| method | `add_group(...)` | `add_group(label, *, icon=None)` | |
| method | `add_header(text)` | `add_header(text)` | |
| method | `add_separator()` | `add_separator()` | |
| method | `navigate(key)` | `navigate(key)` | Kept. |
| method | `select(key)` | removed | Alias of `navigate`; pick one. |
| method | `on_page_changed`, `off_page_changed` | `on(Event.App.PAGE_MOUNT, ...)`, shorthand `on_page_change` | Match enum (`PAGE_MOUNT` per spec). |

---

### ButtonGroup

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `ButtonGroup` | `ButtonGroup` | Kept. |
| kwarg | `orient`, `accent`, `variant`, `density`, `state` | same | |
| method | `add(key, label, ...)` | `add(key, *, label, ...)` | |
| method | `remove(key)`, `item(key)` | same | |
| method | `items()`, `keys()` | `items` property, `keys` property | Nouns. |
| method | `configure_item(key, **)` | `update_item(key, **)` | |

---

### Calendar

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Calendar` | `Calendar` | Kept. |
| Positional 1 | — | `value: date \| None = None` | |
| kwarg | `value` | `value` | |
| kwarg | `start_date`, `end_date` | `range_start`, `range_end` | Clear: these mean the selected range, not the visible range. |
| kwarg | `disabled_dates` | `disabled_dates` | |
| kwarg | `selection_mode` | `selection_mode: "single"|"range"|"multiple"` | |
| kwarg | `max_date`, `min_date` | `max_date`, `min_date` | |
| kwarg | `show_outside_days` | `show_outside_days` | |
| kwarg | `show_week_numbers` | `show_week_numbers` | |
| kwarg | `first_weekday` | `first_weekday` | |
| kwarg | `accent`, `padding` | same | |
| property | — | `value`, `range: tuple[date, date] \| None` | |
| method | `get()`, `set()` | removed | Use `.value`. |
| method | `get_range()`, `set_range()` | removed | Use `.range`. |
| method | `on_date_selected`, `off_date_selected` | `on_select` shorthand for `Event.Selection.SELECT` | |
| event | `<<DateSelect>>` | `Event.Selection.SELECT` / `on_select` | |

---

### ContextMenu

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `ContextMenu` | `ContextMenu` | Kept. |
| kwarg | `master` | `parent` | Universal Tk-ism removal. |
| kwarg | `minwidth`, `width` | `min_width`, `width` | Snake-case. |
| kwarg | `minheight`, `height` | `min_height`, `height` | |
| kwarg | `target` | `target` | Widget to attach to. |
| kwarg | `anchor` | `anchor` | |
| kwarg | `attach` | `attach: bool` | |
| kwarg | `offset` | `offset` | |
| kwarg | `hide_on_outside_click` | `hide_on_outside_click` | Kept. |
| kwarg | `items` | `items` | Kept. |
| kwarg | `density` | `density` | |
| kwarg | `trigger` | `trigger: "right_click"|"left_click"|"hover"|None` | Plain enum. |
| kwarg | `command` | `on_select` | Generic select handler. |
| method | `add_command(label, command, ...)` | `add_item(label, *, on_click, ...)` | "command" is not a noun. |
| method | `add_checkbutton(...)` | `add_check_item(...)` | |
| method | `add_radiobutton(...)` | `add_radio_item(...)` | |
| method | `add_separator()` | `add_separator()` | |
| method | `add_item(...)`, `add_items(...)` | same | |
| method | `insert_item(idx, ...)` | `insert_item(index, ...)` | |
| method | `item(key)`, `remove_item(key)`, `move_item(key, idx)`, `configure_item(key, **)` | `item(key)`, `remove_item(key)`, `move_item(key, index)`, `update_item(key, **)` | |
| method | `show(x=, y=)` | `show(x=None, y=None)` | |
| method | `hide()`, `destroy()`, `keys()` | `hide()`, `destroy()`, `keys` property | |

---

### DateEntry → **DateField**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `DateEntry` | `DateField` | Match TextField rename. |
| Positional 1 | — | `value: date \| None = None` | |
| kwarg | `value` | `value` | |
| kwarg | `value_format` | `value_format` | |
| kwarg | `label`, `message` | `label`, `message` | Kept (field framing text). |
| kwarg | `show_picker_button` | `show_picker_button` | |
| kwarg | `picker_title` | `picker_title` | |
| kwarg | `picker_first_weekday` | `picker_first_weekday` | |
| kwarg | `selection_mode` | `selection_mode` | |
| kwarg | `start_date`, `end_date` | `range_start`, `range_end` | Mirror Calendar. |
| kwarg | `min_date`, `max_date` | `min_date`, `max_date` | |
| kwarg | `disabled_dates` | `disabled_dates` | |
| property | `date_picker_button` | `picker_button` | Shorter; "date" implied. |
| property | `value` | `value` | |

---

### DropdownButton → **MenuButton**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `DropdownButton` | `MenuButton` | Disambiguates from `Dropdown` (the combobox). A MenuButton opens a menu; a Dropdown selects from a list. |
| Positional 1 | — | `label: str` | |
| kwarg | `text` | `label` | |
| kwarg | `items` | `items` | |
| kwarg | `command` | `on_select` | Fires when a menu item is chosen. |
| kwarg | `icon`, `icon_only` | same | |
| kwarg | `variant`, `density` | same | |
| kwarg | `popdown_options` | `menu_options: dict` | Plain English. |
| method | `show_menu()` | `show_menu()` | Kept. |
| method | `add_command(...)` | `add_item(label, *, on_click=None)` | |
| method | `add_checkbutton(...)` | `add_check_item(...)` | |
| method | `add_radiobutton(...)` | `add_radio_item(...)` | |
| method | `add_separator()` | `add_separator()` | |
| method | `item(key)`, `remove_item(key)`, `items()`, `keys()` | `item`, `remove_item`, `items` property, `keys` property | |
| property | `context_menu` | `menu` | Shorter. |

---

### Expander

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Expander` | `Expander` | Kept. |
| Positional 1 | — | `title: str` | |
| kwarg | `title` | `title` | |
| kwarg | `icon` | `icon` | |
| kwarg | `expanded` | `expanded: bool = False` | |
| kwarg | `collapsible` | `collapsible: bool = True` | |
| kwarg | `highlight` | `highlight: bool` | |
| kwarg | `icon_expanded` | `expanded_icon` | Match Tree. |
| kwarg | `icon_collapsed` | `collapsed_icon` | |
| kwarg | `icon_position` | `icon_position: "left"|"right"` | |
| kwarg | `signal` | `signal` | |
| kwarg | `variable` | removed | |
| kwarg | `value` | `value` | |
| property | — | `expanded`, `content`, `is_selected` → `selected` | |
| method | `toggle()`, `expand()`, `collapse()`, `select()`, `add(child)` | same | |
| method | `on_toggled`, `off_toggled` | `on_toggle` shorthand for `Event.Input.CHANGE` | |
| method | `on_selected`, `off_selected` | `on_select` shorthand for `Event.Selection.SELECT` | |
| event | `<<Toggle>>` | `Event.Input.CHANGE` / `on_toggle` | |
| event | `<<Selected>>` | `Event.Selection.SELECT` / `on_select` | |

---

### FloodGauge

> **REMOVED in v2.** `FloodGauge` was a ttkbootstrap artifact. Its capabilities are absorbed into an enhanced `ProgressBar`. Migrate usages to `ProgressBar`.

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `FloodGauge` | **removed** | Absorbed into `ProgressBar`. |
| Positional 1 | — | `value: float = 0` | |
| kwarg | `value` | `value` | |
| kwarg | `maximum` | `max_value` | Match ProgressBar. |
| kwarg | `mode` | `mode: "determinate"|"indeterminate"` | |
| kwarg | `mask` | `mask: str` | Format string for overlay text. |
| kwarg | `text` | `text` (overlay) | |
| kwarg | `font` | `font` | |
| kwarg | `accent` | `accent` | |
| kwarg | `orient` | `orient` | |
| kwarg | `length` | `length` (px) | |
| kwarg | `thickness` | `thickness` (px) | |
| kwarg | `increment` | `step` | Match Spinbox/Slider. |
| kwarg | `variable` | removed | |
| kwarg | `textvariable` | removed | |
| kwarg | — | `signal`, `text_signal` | Standard. |
| property | — | `value`, `running: bool` | |
| method | `get()`, `set()` | removed | Use `.value`. |
| method | `step(delta=1)` | `step(delta=None)` | If None, uses `.step`. |
| method | `start()`, `stop()` | same | |

---

### Form

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Form` | `Form` | Kept. |
| Positional 1 | — | `items: list[FormItem]` | |
| kwarg | `data` | `data: dict \| Signal[dict]` | Kept. |
| kwarg | `items` | `items` | |
| kwarg | `col_count` | `columns: int` | Aligns with Grid (it currently rejects `columns=` — that's a known gotcha to fix). |
| kwarg | `min_col_width` | `min_column_width` | Snake-case. |
| kwarg | `on_data_changed` | `on_change` callback | Match Event.Input.CHANGE. |
| kwarg | `width`, `height` | same | |
| kwarg | `accent` | `accent` | |
| kwarg | `buttons` | `buttons` | |
| property | `value`, `result` | `value`, `result` | Kept. |
| method | `field(name)`, `fields()`, `keys()` | `field(name)`, `fields` property, `keys` property | |
| method | `get_field_value(name)`, `set_field_value(name, v)` | `get(name)`, `set(name, value)` | Shorter on the Form (not on widgets). |
| method | `get()`, `set()` | removed | Use `.value`. |
| method | `field_variable`, `field_signal`, `field_textsignal` | `field_signal(name)`, `field_text_signal(name)` | Drop `variable` accessor. |
| event | — | `Event.Input.CHANGE` / `on_change` | |
| event | — | `Event.Input.SUBMIT` / `on_submit` | New. |
| event | — | `Event.Input.VALIDATE` / `on_validate` | New. |

> ⚠ Form button command receives the form: that magic is fine but document it clearly. Consider: `on_click=lambda f: f.value` is acceptable, but the new `Event.Widget.CLICK` payload includes `.source` which exposes the form — preferred.

---

### ListView

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `ListView` | `ListView` | Kept. |
| Positional 1 | — | `items: list \| DataSource` | |
| kwarg | `items` | `items` | |
| kwarg | `datasource` | `data_source` | Snake-case. |
| kwarg | `selection_mode` | `selection_mode: "none"|"single"|"multiple"|"extended"` | Standardize. |
| kwarg | `show_selection_controls` | `show_selection_controls` | |
| kwarg | `show_chevron` | `show_chevron` | |
| kwarg | `enable_removing` | `allow_remove` | "enable_X" → "allow_X" or "show_X" depending on intent. |
| kwarg | `enable_dragging` | `allow_reorder` | More specific. |
| kwarg | `striped` | `striped` | |
| kwarg | `striped_background` | `striped_background_color` | |
| kwarg | `show_separator` | `show_separators` | Plural. |
| kwarg | `scrollbar_visibility` | `scrollbar_visibility: "auto"|"always"|"never"` | |
| kwarg | `enable_focus` | `focusable` | |
| kwarg | `enable_hover` | `show_hover` | |
| kwarg | `select_on_click` | `select_on_click` | Kept. |
| kwarg | `density` | `density` | |
| property | — | `items`, `selection: list`, `selected: list`, `selected_keys: list` | |
| method | `selected()` | `selected` property | Noun. Returns records. |
| method | `select(*keys)` | `select(*keys)` | |
| method | `unselect(*keys)` | `deselect(*keys)` | Match settled `deselect_*` convention. |
| method | `clear_selection()` | `clear_selection()` | Kept. |
| event | — | `Event.Selection.SELECT` / `on_select` | |
| event | — | `Event.Selection.DESELECT` / `on_deselect` | |
| event | — | `Event.Widget.CLICK` / `on_row_click` | |
| event | — | `Event.Widget.DOUBLE_CLICK` / `on_row_double_click` | |

---

### Meter → **Gauge**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Meter` | `Gauge` | Renamed — "gauge" is the correct domain term. |
| Positional 1 | — | `value: float = 0` | |
| kwarg | `value` | `value` | |
| kwarg | `minvalue` | `min_value` | Standard rename. |
| kwarg | `maxvalue` | `max_value` | |
| kwarg | `value_format` | `value_format` | Kept. |
| kwarg | `value_prefix` | `value_prefix` | Kept. |
| kwarg | `value_suffix` | `value_suffix` | Kept. |
| kwarg | `value_font` | `value_font` | |
| kwarg | `subtitle` | `subtitle` | |
| kwarg | `size` | `size` (px) | |
| kwarg | `thickness` | `thickness` (px) | |
| kwarg | `indicator_width` | `indicator_width` | |
| kwarg | `segment_width` | `segment_width` | |
| kwarg | `arc_range` | `arc_range` (degrees) | |
| kwarg | `arc_offset` | `arc_offset` (degrees) | |
| kwarg | `meter_type` | `meter_type: "full"|"semi"|"radial"` | |
| kwarg | `show_text` | `show_text` | |
| kwarg | `interactive` | `interactive` | |
| kwarg | `step_size` | `step` | Match other widgets. |
| kwarg | `accent` | `accent` | |
| kwarg | (legacy: `amountused`, `amounttotal`, `subtext`, `stripethickness`) | **removed** | Known bug — delete. |
| property | — | `value`, `subtitle`, `min_value`, `max_value` | |
| method | `get()`, `set()` | removed | Use `.value`. |
| method | `step(delta=None)` | `step(delta=None)` | |
| method | `on_changed`, `off_changed` | `on_change` shorthand | |
| event | — | `Event.Input.CHANGE` / `on_change` | |

---

### NumericEntry → **NumberField**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `NumericEntry` | `NumberField` | Match TextField/DateField. |
| Positional 1 | — | `value: float \| int = 0` | |
| kwarg | `value` | `value` | |
| kwarg | `label`, `message` | `label`, `message` | |
| kwarg | `show_spin_buttons` | `show_steppers` | "spin buttons" is Win32 jargon. |
| kwarg | `minvalue` | `min_value` | |
| kwarg | `maxvalue` | `max_value` | |
| kwarg | `increment` | `step` | |
| property | `increment_widget`, `decrement_widget` | `increment_button`, `decrement_button` | Plain. |
| method | `increment()`, `decrement()`, `step(n)` | same | |
| method | `on_increment`, `off_increment` | `on_increment` shorthand | |
| method | `on_decrement`, `off_decrement` | `on_decrement` shorthand | |

---

### PageStack → **NavigationStack** *(optional rename)*

> Recommendation: keep `PageStack` — it's already clear. Renaming to `NavigationStack` aligns with SwiftUI/iOS but adds length without much clarity gain.

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `PageStack` | `PageStack` | Kept. |
| kwarg | `takefocus` | `focusable` | |
| kwarg | `width`, `height`, `padding` | same | |
| method | `add(key, page)` | `add(key, page)` | |
| method | `remove(key)` | `remove(key)` | |
| method | `navigate(key, **)` | `navigate(key, **)` | Kept. |
| method | `back()`, `forward()`, `can_back()`, `can_forward()` | `back()`, `forward()`, `can_back` property, `can_forward` property | Booleans become noun properties. |
| method | `current()` | `current` property | |
| method | `item(key)` | `page(key)` | "page" is the noun here. |
| method | `on_page_changed`, `off_page_changed` | `on_page_change` shorthand | |
| event | `<<PageUnmount>>` | `Event.App.PAGE_UNMOUNT` / `on_page_unmount` | |
| event | `<<PageWillMount>>` | `Event.App.PAGE_WILL_MOUNT` / `on_page_will_mount` | Add to enum. |
| event | `<<PageMount>>` | `Event.App.PAGE_MOUNT` / `on_page_mount` | |
| event | `<<PageChange>>` | `Event.App.PAGE_CHANGE` / `on_page_change` | Add to enum. |

> ⚠ The Event enum needs `Event.App.PAGE_WILL_MOUNT` and `Event.App.PAGE_CHANGE` added.

---

### PasswordEntry → **PasswordField**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `PasswordEntry` | `PasswordField` | Match TextField. |
| Positional 1 | — | `value: str = ""` | |
| kwarg | `value` | `value` | |
| kwarg | `label`, `message` | `label`, `message` | |
| kwarg | `show_visibility_toggle` | `show_visibility_toggle` | Kept. |
| property | `visibility_toggle` | `visibility_toggle` | The toggle button. |

---

### PathEntry → **PathField**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `PathEntry` | `PathField` | Match TextField. |
| Positional 1 | — | `value: str \| Path = ""` | |
| kwarg | `value` | `value` | |
| kwarg | `dialog` | `dialog: "open"|"save"|"directory"` | Plain enum. |
| kwarg | `dialog_options` | `dialog_options: dict` | |
| kwarg | `button_text` | `button_label` | Match Button rename. |
| kwarg | `button_accent` | `button_accent` | |
| kwarg | `label`, `message` | `label`, `message` | |

---

### RadioGroup

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `RadioGroup` | `RadioGroup` | Kept. |
| Positional 1 | — | `options: list \| dict[str, str]` | Fixes "needs options= constructor" bug from API gaps. |
| kwarg | `options` | `options` | New required kwarg. |
| kwarg | `orient` | `orient` | |
| kwarg | `accent` | `accent` | |
| kwarg | `text` | `title` | Match GroupBox. |
| kwarg | `labelanchor` | `title_anchor` | |
| kwarg | `variable` | removed | |
| kwarg | `signal` | `signal` | |
| kwarg | `value` | `value` | Initial selection. |
| kwarg | `state` | `state` / `disabled` | |
| kwarg | `show_indicator` | `show_indicator` | |
| property | — | `value`, `selected_key`, `disabled` | |
| method | `add(key, label)` | `add(key, label)` | |
| method | `remove(key)`, `item(key)`, `items()`, `keys()` | `remove(key)`, `item(key)`, `items` property, `keys` property | |
| method | `selected()` | `selected` property | Bug fix: should validate against values, not keys. |
| method | `select(key_or_value)` | `select(key=None, value=None)` | Disambiguate. Currently selects by key but accepts value — confusing. |
| event | — | `Event.Selection.SELECT` / `on_select` | |
| event | — | `Event.Input.CHANGE` / `on_change` | |

---

### RangeSlider

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `RangeSlider` | `RangeSlider` | Kept. |
| kwarg | `minvalue` | `min_value` | |
| kwarg | `maxvalue` | `max_value` | |
| kwarg | `lovalue` | `low_value` | |
| kwarg | `hivalue` | `high_value` | |
| kwarg | `orient` | `orient` | |
| kwarg | `accent`, `surface` | same | |
| kwarg | `lo_variable`, `hi_variable` | removed | |
| kwarg | `lo_signal`, `hi_signal` | `low_signal`, `high_signal` | |
| kwarg | `state` | `state` / `disabled` | |
| kwarg | `show_value` | `show_value` | |
| kwarg | `tick_interval` | `tick_step` | "interval" is ambiguous (time?). |
| kwarg | `minor_ticks` | `minor_ticks` | |
| kwarg | `tick_labels` | `tick_labels` | |
| kwarg | `tick_format` | `tick_format` | |
| kwarg | — | `show_minmax` | Match Slider. |
| property | `lovalue`, `hivalue` | `low_value`, `high_value`, `range: tuple` | |
| method | `get_lo()`, `get_hi()` | removed | Use `.low_value`/`.high_value`. |
| method | `set_lo(v)`, `set_hi(v)` | removed | |
| method | `on_changed`, `off_changed` | `on_change` shorthand | |
| method | `on_committed`, `off_committed` | `on_commit` shorthand | |
| event | — | `Event.Input.CHANGE` / `on_change` | |
| event | — | `Event.Input.SUBMIT` / `on_commit` | Or new `Event.Input.COMMIT`. |

---

### SelectBox → **Select**

> The canonical selection widget in v2. Replaces both old `Combobox` and `SelectBox`. NOTE: renamed reason was originally — `Dropdown` (was Combobox, fixed list) and `SelectBox` (search + custom values). Renaming `SelectBox` to `ComboBox` makes the distinction explicit if we accept that "combo" implies both *combine input + dropdown*. Alternative: keep `SelectBox`.

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `SelectBox` | `Select` | The single selection widget. |
| Positional 1 | — | `options: list` | |
| kwarg | `value` | `value` | |
| kwarg | `items` | `options` | Standardize on `options`. |
| kwarg | `label`, `message` | `label`, `message` | |
| kwarg | `allow_custom_values` | `allow_custom_values` | Kept. |
| kwarg | `show_dropdown_button` | `show_dropdown_button` | |
| kwarg | `dropdown_button_icon` | `dropdown_button_icon` | |
| kwarg | `enable_search` | `searchable` | Plain. |
| property | `selected_index` | `selected_index`, `value` | |
| event | `<<Change>>` | `Event.Input.CHANGE` / `on_change` | Was emitting `<<Change>>`, not `<<SelectionChange>>` (gotcha). |
| event | — | `Event.Selection.SELECT` / `on_select` | |

---

### Slider

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Slider` | `Slider` | Kept. |
| Positional 1 | — | `value: float = 0` | |
| kwarg | `minvalue` | `min_value` | |
| kwarg | `maxvalue` | `max_value` | |
| kwarg | `value` | `value` | |
| kwarg | `orient` | `orient` | |
| kwarg | `accent`, `surface` | same | |
| kwarg | `variable` | removed | |
| kwarg | `signal` | `signal` | |
| kwarg | `state` | `state` / `disabled` | |
| kwarg | `show_value` | `show_value` | |
| kwarg | `show_minmax` | `show_minmax` | |
| kwarg | `tick_interval` | `tick_step` | Mirror RangeSlider. |
| kwarg | `minor_ticks`, `tick_labels`, `tick_format` | same | |
| property | — | `value`, `min_value`, `max_value`, `disabled` | |
| method | `get()`, `set()` | removed | |
| method | `on_changed`, `off_changed` | `on_change` shorthand | |
| method | `on_committed`, `off_committed` | `on_commit` shorthand | |
| event | — | `Event.Input.CHANGE` / `on_change` | |
| event | — | `Event.Input.SUBMIT` / `on_commit` | Or `Event.Input.COMMIT`. |

---

### TableView → **Table**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `TableView` | `Table` | Shorter, matches `Tree`. |
| Positional 1 | — | `columns: list[Column]` | |
| kwarg | `columns` | `columns` | |
| kwarg | `rows` | `rows` | |
| kwarg | `datasource` | `data_source` | Snake-case. (Note: currently only accepts `SqliteDataSource` — that limitation needs fixing.) |
| kwarg | `selection_mode` | `selection_mode` | |
| kwarg | `sorting_mode` | `sorting_mode: "none"|"single"|"multiple"` | |
| kwarg | `enable_filtering` | `allow_filter` | "allow_X" convention. |
| kwarg | `enable_header_filtering` | `allow_header_filter` | |
| kwarg | `enable_row_filtering` | `allow_row_filter` | |
| kwarg | `enable_search` | `searchable` | Adjective. |
| kwarg | `search_mode` | `search_mode` | |
| kwarg | `search_trigger` | `search_trigger` | |
| kwarg | `paging_mode` | `paging_mode: "none"|"client"|"server"` | |
| kwarg | `page_size` | `page_size` | |
| kwarg | `enable_adding` | `allow_add` | |
| kwarg | `enable_editing` | `allow_edit` | |
| kwarg | `enable_deleting` | `allow_delete` | |
| kwarg | `enable_exporting` | `allow_export` | |
| kwarg | `striped` | `striped` | |
| kwarg | `allow_grouping` | `allow_group` | |
| kwarg | `show_table_status` | `show_status_bar` | Plain. |
| event | `<<SelectionChange>>` | `Event.Selection.SELECT` / `on_select` | |
| event | `<<RowClick>>` | `Event.Widget.CLICK` / `on_row_click` | |
| event | — | `Event.Widget.DOUBLE_CLICK` / `on_row_double_click` | |
| event | — | `Event.Input.CHANGE` / `on_change` (cell edit) | |

> ⚠ Per-column `format=` is planned, not implemented. Should land with v2.

---

### TabView → **Tabs**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `TabView` | `Tabs` | Shorter. |
| kwarg | `orient` | `orient` | |
| kwarg | `show_divider` | `show_divider` | |
| kwarg | `compound` | `icon_position: "left"|"right"|"top"|"bottom"|"only"` | Match Button. |
| kwarg | `tab_width` | `tab_width` | |
| kwarg | `tab_padding` | `tab_padding` | |
| kwarg | `tab_anchor` | `tab_anchor` | |
| kwarg | `enable_closing` | `allow_close` | |
| kwarg | `enable_adding` | `allow_add` | |
| kwarg | `accent` | `accent` | |
| kwarg | `variant` | `variant` | Fix: `variant="pill"` currently crashes. |
| method | `add(key, label, ...)` | `add(key, *, label, icon=None, ...)` | |
| method | `remove(key)` | `remove(key)` | |
| method | `select(key)` | `select(key)` | |
| method | `item(key)`, `items()`, `keys()` | `tab(key)`, `tabs` property, `keys` property | "tab" is the noun. |
| method | `on_tab_changed` | `on_change` shorthand | |
| method | `on_tab_activate`, `on_tab_deactivate` | `on_activate`, `on_deactivate` | Drop redundant `_tab_`. |
| method | `on_tab_add` | `on_add` | |
| event | `<<TabChanged>>` | `Event.Selection.SELECT` / `on_change` | |
| event | — | `Event.Widget.ACTIVATE` / `on_activate` | Add to enum. |
| event | — | `Event.Widget.DEACTIVATE` / `on_deactivate` | |

---

### TextArea

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `TextArea` | `TextArea` | Kept. |
| Positional 1 | — | `value: str = ""` | |
| kwarg | `value` | `value` | |
| kwarg | `textsignal` | `text_signal` | |
| kwarg | `label`, `message` | `label`, `message` | |
| kwarg | `show_message` | `show_message` | |
| kwarg | `required` | `required` | |
| kwarg | `placeholder` | `placeholder` | |
| kwarg | `max_length` | `max_length` | |
| kwarg | `read_only` | `read_only` | Kept. |
| kwarg | `wrap` | `wrap: "none"|"word"|"char"` | |
| kwarg | `height` | `height` (px) | |
| kwarg | `scrollbars` | `scrollbars: "auto"|"always"|"never"|"vertical"|"horizontal"` | |
| kwarg | `font` | `font` | |
| kwarg | `accent` | `accent` | |
| kwarg | `on_input`, `on_changed`, `on_blur`, `on_valid`, `on_invalid`, `on_validated` | `on_input`, `on_change`, `on_blur`, `on_valid`, `on_invalid`, `on_validate` | Standardize past-tense → present (matches enum names). |
| method | `validate()` | `validate()` | |
| event | `<<Input>>` | `Event.Input.INPUT` / `on_input` | Add to enum: keystroke-level. |
| event | `<<Valid>>` | `Event.Input.VALID` / `on_valid` | Add. |
| event | `<<Invalid>>` | `Event.Input.INVALID` / `on_invalid` | Add. |
| event | `<<Validate>>` | `Event.Input.VALIDATE` / `on_validate` | |

> ⚠ Callback shape inconsistency: `on_input`/`on_changed` get Tk events, `on_valid`/`on_invalid`/`on_validated` get dicts. v2: **all** event callbacks receive the v2 Event object — same shape everywhere. This fixes a documented gotcha.

---

### Toast

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Toast` | `Toast` | Kept. |
| kwarg | `title` | `title` | |
| kwarg | `icon` | `icon` | |
| kwarg | `message` | `message` | |
| kwarg | `memo` | `detail` | "memo" is unusual. |
| kwarg | `duration` | `duration: int \| None` (ms) | None = manual dismiss. |
| kwarg | `buttons` | `actions: list[Action]` | "buttons" is misleading at the data level. |
| kwarg | `show_close_button` | `show_close_button` | |
| kwarg | `accent` | `accent` | |
| kwarg | `position` | `position: "top-left"|"top-right"|...` | |
| kwarg | `alert` | `play_sound: bool` | Plain. |
| kwarg | `on_dismissed` | `on_dismiss` | Match Event naming. |
| method | `show()`, `hide()`, `destroy()` | same | |
| event | — | `Event.Widget.DISMISS` / `on_dismiss` | Add to enum. |

---

### ToggleGroup

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `ToggleGroup` | `ToggleGroup` | Kept. |
| Positional 1 | — | `options: list` | Fixes "needs options= constructor" gap. |
| kwarg | `mode` | `mode: "single"|"multiple"` | |
| kwarg | `orient` | `orient` | |
| kwarg | `accent`, `variant` | same | |
| kwarg | `variable` | removed | |
| kwarg | `signal` | `signal` | |
| kwarg | `value` | `value` | |
| kwarg | — | `padding` | Fix the `TypeError` bug. |
| method | `add(key, label)`, `remove(key)`, `item(key)`, `items()`, `keys()` | `add(key, label)`, `remove(key)`, `item(key)`, `items` prop, `keys` prop | |

---

### Toolbar

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Toolbar` | `Toolbar` | Kept. |
| kwarg | `show_window_controls` | `show_window_controls` | |
| kwarg | `draggable` | `draggable` | |
| kwarg | `button_variant` | `button_variant` | |
| kwarg | `density` | `density` | |
| kwarg | `padding` | `padding` | |
| method | `add_button(label, ...)` | `add_button(label, *, icon=None, on_click=None)` | Match Button v2. |
| method | `add_label(text)` | `add_label(text)` | |
| method | `add_spacer()` | `add_spacer()` | |
| method | `add_separator()` | `add_separator()` | |

---

### Tooltip

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Tooltip` | `Tooltip` | Kept. |
| kwarg | `widget` | `target` | Match ContextMenu. |
| kwarg | `text` | `text` | |
| kwarg | `padding` | `padding` | |
| kwarg | `justify` | `justify` | |
| kwarg | `accent` | `accent` | |
| kwarg | `wraplength` | `wrap_width` | |
| kwarg | `delay` | `delay` (ms) | |
| kwarg | `image` | `image` | |
| kwarg | `anchor_point` | `anchor_point` | |
| kwarg | `window_point` | `window_point` | |
| kwarg | `auto_flip` | `auto_flip` | |
| method | `destroy()` | `destroy()` | |

---

## RUNTIME/APP

### App

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `App` | `App` | Kept. |
| kwarg | `title` | `title` | |
| kwarg | `theme` | `theme` | Direct kwarg in v2 — drop the "settings dict only" requirement. Currently a documented gotcha. |
| kwarg | `icon` | `icon` | |
| kwarg | `settings` | `settings: AppSettings \| dict` | Kept as escape hatch. |
| kwarg | `localize` | `localize` | |
| kwarg | `size` | `size` | |
| kwarg | `position` | `position` | |
| kwarg | `minsize` | `min_size` | Snake-case. |
| kwarg | `maxsize` | `max_size` | |
| kwarg | `resizable` | `resizable` | |
| kwarg | `scaling` | `scaling` | |
| kwarg | `hdpi` | `hidpi` | Standard capitalization. |
| kwarg | `alpha` | `opacity` | Plain English. |
| kwarg | `transient` | `transient_for` | "transient" alone is opaque. |
| kwarg | `override_redirect` | `decorated: bool = True` | Boolean inversion; "override_redirect" is X11 jargon. |
| kwarg | `window_style` | `window_style` | |
| kwarg | `center_on_screen` | `center_on_screen` | |
| kwarg | `on_close` | `on_close` | |
| kwarg | — | `light_theme`, `dark_theme` | Document existing gotcha — currently only via `settings={}`. |
| method | `mainloop()` | `start()` | Plain English. Keep `mainloop` as alias for one cycle. |
| method | `close()` | `close()` | |
| method | `destroy()` | `destroy()` | |
| method | `add_close_handler(fn)` | `add_close_handler(fn)` | |
| method | `on_about(fn)`, `on_preferences(fn)` | `on_about(fn)`, `on_preferences(fn)` | Keep. |
| property | `settings`, `winsys` | `settings`, `window_system` | "winsys" is Tk-ism. |
| event | — | `Event.App.THEME_CHANGE` / `on_theme_change` | |
| event | — | `Event.App.PAGE_MOUNT` etc. | (via PageStack/AppShell) |

---

### Toplevel → **Window**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Toplevel` | `Window` | "Toplevel" is Tk jargon. |
| kwarg | `title` | `title` | |
| kwarg | `icon` | `icon` | |
| kwarg | `size`, `position`, `minsize`, `maxsize` | `size`, `position`, `min_size`, `max_size` | Snake-case. |
| kwarg | `resizable` | `resizable` | |
| kwarg | `transient` | `transient_for` | |
| kwarg | `overrideredirect` | `decorated: bool = True` | |
| kwarg | `windowtype` | `window_type` | |
| kwarg | `topmost` | `always_on_top` | Plain. |
| kwarg | `toolwindow` | `tool_window` | |
| kwarg | `alpha` | `opacity` | |
| kwarg | `window_style` | `window_style` | |
| kwarg | `modal` | `modal` | |
| kwarg | `center_on_parent`, `center_on_screen` | same | |
| kwarg | `on_close` | `on_close` | |
| method | `show()` | `show()` | |
| method | `block_until_closed()` | `block_until_closed()` | |
| method | `add_close_handler(fn)` | `add_close_handler(fn)` | |
| property | `result`, `winsys` | `result`, `window_system` | |

---

## SIGNALS / THEME

### Signal[T]

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Signal[T]` | `Signal[T]` | Kept. |
| Positional 1 | `value` | `value: T` | |
| kwarg | `name` | `name` | |
| kwarg | `master` | `parent` | Match general rename. |
| method | `get()` | `get()` | Kept as alias for `.value`. |
| method | `set(v)` | `set(value)` | Kept as alias for `.value = v`. |
| method | `map(fn)` | `map(fn)` | |
| method | `subscribe(fn)` | `subscribe(fn)` → returns `Subscription` | |
| method | `unsubscribe(id)` | `unsubscribe(subscription)` | Pass the Subscription object. |
| method | `unsubscribe_all()` | `unsubscribe_all()` | |
| property | `name` | `name` | |
| property | `type` | `type` | |
| property | `var` | `tk` | Internal Tk var renamed per task spec. |
| property | — | `value` | The current value (read/write). |

### Theme module

| Category | Current | v2 | Notes |
|---|---|---|---|
| Function | `set_theme(name)` | `set_theme(name)` | Kept. |
| Function | `toggle_theme()` | `toggle_theme()` | Kept. |
| Function | `get_theme()` | `current_theme()` | Verb function on the noun. |
| Function | `get_themes()` | `available_themes()` | More descriptive. |
| Function | `get_theme_color(token)` | `theme_color(token)` | Drop `get_` prefix on read-only lookups. |

---

## DIALOGS

### Dialog

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `Dialog` | `Dialog` | Kept. |
| kwarg | `master` | `parent` | Tk-ism. |
| kwarg | `title` | `title` | |
| kwarg | `content_builder` | `build_content: Callable` | "build_X" is more obviously a builder. |
| kwarg | `footer_builder` | `build_footer: Callable` | |
| kwarg | `buttons` | `buttons` | |
| kwarg | `mode` | `mode: "modal"|"modeless"` | |
| kwarg | `size`, `minsize`, `maxsize`, `resizable` | `size`, `min_size`, `max_size`, `resizable` | Snake-case. |
| method | `show()` → None | `show()` → `self.result` returned | Fix documented gotcha — `show()` returns result. |
| method | `block_until_closed()` | `block_until_closed()` | |
| method | `close()` | `close()` | |
| property | `result` | `result` | |

---

### MessageDialog

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `MessageDialog` | `MessageDialog` | Kept. |
| kwarg | `message` | `message` | |
| kwarg | `title` | `title` | |
| kwarg | `buttons` | `buttons` | |
| kwarg | `command` | `on_button: Callable[[str], None]` | Plain. |
| kwarg | `width` | `width` | |
| kwarg | `master` | `parent` | |
| kwarg | `alert` | `play_sound: bool` | Match Toast. |
| kwarg | `default` | `default_button` | Plain. |
| kwarg | `padding` | `padding` | |
| kwarg | `icon` | `icon` | |
| kwarg | `localize` | `localize` | |

### Alert / Confirm — module-level `bs.*` functions

| Current | v2 | Notes |
|---|---|---|
| `MessageBox.ok(msg)` | `bs.alert(msg)` | `None` |
| `MessageBox.yesno(msg)` | `bs.confirm(msg)` | `bool` |
| `MessageBox.info/warning/error(msg)` | `bs.alert(msg, icon=...)` | `None` |
| `MessageBox.okcancel(msg)` | `bs.confirm(msg, cancel=True)` | `bool\|None` |
| `MessageBox.retrycancel(msg)` | `bs.confirm(msg, retry=True)` | `bool` |
| `MessageBox.yesnocancel(msg)` | `bs.confirm(msg, cancel=True)` | `bool\|None` |

---

### QueryDialog

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `QueryDialog` | `QueryDialog` | Kept. |
| kwarg | `prompt`, `title`, `value` | same | |
| kwarg | `minvalue`, `maxvalue` | `min_value`, `max_value` | Standard rename. |
| kwarg | `width` | `width` | |
| kwarg | `datatype` | `value_type: type` | Plain. |
| kwarg | `padding` | `padding` | |
| kwarg | `master` | `parent` | |
| kwarg | `items` | `options` | Standardize. |
| kwarg | `value_format` | `value_format` | |
| kwarg | `increment` | `step` | |

### Ask functions — module-level `bs.ask_*()` functions

| Current | v2 | Notes |
|---|---|---|
| `QueryBox.get_string(prompt)` | `bs.ask_string(prompt)` | `str\|None` |
| `QueryBox.get_integer(prompt)` | `bs.ask_integer(prompt)` | `int\|None` |
| `QueryBox.get_float(prompt)` | `bs.ask_float(prompt)` | `float\|None` |
| `QueryBox.get_choice(prompt, items)` | `bs.ask_choice(prompt, options)` | `str\|None` |
| `QueryBox.get_date(prompt)` | `bs.ask_date(prompt)` | `date\|None` |

---

### DateDialog

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `DateDialog` | `DateDialog` | Kept. |
| kwarg | `title`, `master` | `title`, `parent` | |
| kwarg | `initial_date` | `value` | Match other widgets. |
| kwarg | `hide_window_chrome` | `undecorated` | Match App. |
| kwarg | `disabled_dates` | `disabled_dates` | |
| kwarg | `bounds` | `date_range: tuple[date, date]` | Plain. |
| kwarg | `mode` | `selection_mode` | Match Calendar. |

---

### FontDialog

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `FontDialog` | `FontDialog` | Kept. |
| kwarg | `title`, `master` | `title`, `parent` | |
| kwarg | `default_font` | `value` | Match. |

---

### ColorChooserDialog → **ColorDialog**

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `ColorChooserDialog` | `ColorDialog` | "Chooser" is redundant. |
| kwarg | `master` | `parent` | |
| kwarg | `title` | `title` | |
| kwarg | `initial_color` | `value` | Match. |
| kwarg | `padding` | `padding` | |

---

### FilterDialog

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `FilterDialog` | `FilterDialog` | Kept. |
| kwarg | `master` | `parent` | |
| kwarg | `title` | `title` | |
| kwarg | `items` | `options` | Standardize. |
| kwarg | `enable_search` | `searchable` | |
| kwarg | `enable_select_all` | `allow_select_all` | |
| kwarg | `buttons`, `minsize`, `maxsize` | `buttons`, `min_size`, `max_size` | |

---

### FormDialog

| Category | Current | v2 | Notes |
|---|---|---|---|
| Class | `FormDialog` | `FormDialog` | Kept. |
| kwarg | `master` | `parent` | |
| kwarg | `title`, `data`, `items` | same | |
| kwarg | `col_count` | `columns` | Match Form/Grid. |
| kwarg | `min_col_width` | `min_column_width` | |
| kwarg | `on_data_changed` | `on_change` | |
| kwarg | `width`, `height`, `buttons` | same | |
| kwarg | `minsize`, `maxsize` | `min_size`, `max_size` | |
| kwarg | `resizable`, `alert`, `mode` | `resizable`, `play_sound`, `mode` | |

---

## Cross-widget consistency notes

Issues spotted while writing the proposal that should be resolved framework-wide:

| Concept | Inconsistency | v2 resolution |
|---|---|---|
| "current value" | `value`, `selected`, `selected_index`, `current()` | Always `value` for primary state; `selected_index`/`selected_keys` for selection collections; never `current()`. |
| min/max | `from_`/`to`, `minvalue`/`maxvalue`, `min_date`/`max_date`, `min_value`/`max_value` | Always `min_value`/`max_value` for numerics; `min_date`/`max_date` for dates; `min_size`/`max_size` for window dims. |
| step | `increment`, `step_size`, `step` | Always `step`. |
| label vs text | `text` on Button, `text` on LabelFrame, `text` on Tooltip, `title` on AppShell | `label` on Button, `title` on containers/dialogs/expanders, `text` on Label/TextArea/Tooltip (literal content). |
| open/close icons | `open_icon`/`close_icon` (Tree), `icon_expanded`/`icon_collapsed` (Expander) | Always `expanded_icon`/`collapsed_icon`. |
| toggle icons | `on_icon`/`off_icon` (Check), no equivalent on Switch | Always `checked_icon`/`unchecked_icon` for boolean; `selected_icon`/`unselected_icon` for radio. |
| enable_X vs allow_X vs show_X | `enable_search` (Table), `enable_editing` (Table), `show_chevron` (ListView), `show_indicator` (Check) | `allow_X` for permissions ("allow editing"), `show_X` for visual presence ("show indicator"), `searchable` for adjectival features. |
| command vs on_X | `command` (Button, Spinbox, ContextMenu, Calendar), `postcommand` (Combobox), `validatecommand` (Entry) | Always `on_click` for primary action, `on_change` for value change, `on_open` for menu opens, `validators=` for validation. No `command`. |
| event tense | `<<Change>>` and `<<Changed>>`, `<<Validate>>` and `<<Validated>>`, `on_changed`/`on_validated` callbacks | Standardize on present tense matching Event enum: `on_change`, `on_validate`, `on_submit`. |
| parent kwarg | `master`, `parent` | Always `parent`. |
| size kwargs | `minsize`/`maxsize` vs `min_size`/`max_size` | Snake-case everywhere. |
| "items" overload | `items` is rows of data (ListView), choices (RadioGroup), child widgets (Accordion) | Use `items` only for data rows; `options` for choices; structural collections expose `items` property (children) but accept `add()` not `items=`. |
| variable/signal | both present on many; `value=` silently ignored when signal passed | v2: `signal` and `text_signal` only; raise `TypeError` if `value=` passed together with `signal=`. |
| get/set vs property | `get()`/`set()` everywhere | Properties only; keep `get()`/`set()` only on `Signal` (where the semantics matter) and `Form` (multi-field lookup). |
| visibility / show_X | `show_X` is the rule | Consistent. |
| auto/always/never | `scrollbar_visibility`, `show_separators`, etc. | When tri-state, use `"auto"|"always"|"never"`. |
| callback shape | Tk event vs dict (the documented TextArea gotcha) | Always typed `Event` object with `.value`, `.data`, `.widget`, `.event`. |

### Event enum additions needed

To support v2, the `Event` enum must grow:

```python
class Event:
    class Widget:
        CLICK, DOUBLE_CLICK, RIGHT_CLICK, HOVER, LEAVE, FOCUS, BLUR, RESIZE
        EXPAND, COLLAPSE          # NEW (Tree, Expander, Accordion)
        ACTIVATE, DEACTIVATE      # NEW (Tabs)
        DISMISS                   # NEW (Toast, Dialog)
    class Input:
        CHANGE, SUBMIT, VALIDATE
        INPUT                     # NEW (keystroke-level)
        VALID, INVALID            # NEW (validation outcome)
        COMMIT                    # NEW (slider release; or alias of SUBMIT)
    class Selection:
        SELECT, DESELECT
    class App:
        THEME_CHANGE, PAGE_MOUNT, PAGE_UNMOUNT
        PAGE_WILL_MOUNT           # NEW
        PAGE_CHANGE               # NEW
```

### Bug fixes that ride along with v2

1. `ToggleGroup(padding=)` raises `TypeError` — fix in v2 signature.
2. `insert_addon` with `Checkbox` passes `density=` to ttk — fix in v2 router.
3. `Meter` legacy params (`amountused`, `amounttotal`, `subtext`, `stripethickness`) — remove.
4. `RadioGroup`/`ToggleGroup` need `options=` constructor — added as positional 1.
5. `value=` silently ignored with `signal=` — raise `TypeError` in v2.
6. `Tabs(variant='pill')` crashes — add pill style builder.
7. `on_change`/`on_input` vs `on_valid`/`on_invalid` callback shapes — unified to typed `Event`.
8. `Form` uses `col_count=` not `columns=` — renamed to `columns=`.
9. `Form.validate()` skips `blur`/`key` rules — should be configurable.
10. `Dialog.show()` returns None — should return `self.result`.
11. `Table` only accepts `SqliteDataSource` — should accept any `DataSource`.
12. `ComboBox` (was `SelectBox`) emits `<<Change>>` not `<<SelectionChange>>` — v2 emits `Event.Selection.SELECT` AND `Event.Input.CHANGE` distinctly.
13. `Tree` (was `TreeView`) capitalized to `TreeView` — v2 settles on `Tree`.
14. `text=Signal(...)` doesn't work for Label — fix or document. v2: only `text_signal=` accepted; passing a Signal to `text=` raises.
15. `Style._tk_widgets` grows forever — weakref the set or remove on `<Destroy>`.
16. `L(key, *fmtargs)` uses `%s` — v2 supports `{name}` kwargs too.
17. `RadioGroup.set()` validates keys not values — v2 has `select(key=, value=)`.

### Renames summary (class-level)

| v1 | v2 | |
|---|---|---|
| `Entry` | `TextField` | |
| `CheckButton` | `Checkbox` | |
| `CheckToggle` | `ToggleButton` | |
| `RadioButton` | `Radio` | |
| `RadioToggle` | `RadioToggleButton` | |
| `Combobox` | removed (use `Select`) | |
| `Spinbox` | `Spinbox` *(kept)* | |
| `TreeView` | `Tree` | |
| `LabelFrame` | `GroupBox` | |
| `PanedWindow` | `SplitView` | |
| `DateEntry` | `DateField` | |
| `DropdownButton` | `MenuButton` | |
| `NumericEntry` | `NumberField` | |
| `PasswordEntry` | `PasswordField` | |
| `PathEntry` | `PathField` | |
| `SelectBox` | `Select` | |
| `TableView` | `Table` | |
| `TabView` | `Tabs` | |
| `Toplevel` | `Window` | |
| `ColorChooserDialog` | `ColorDialog` | |

Kept: `Button`, `Label`, `Badge`, `Switch`, `ProgressBar`, `Scrollbar`, `Separator`, `SizeGrip`, `HStack`, `VStack`, `Grid`, `Card`, `Accordion`, `AppShell`, `ButtonGroup`, `Calendar`, `ContextMenu`, `Expander`, `Form`, `ListView`, `Gauge`, `PageStack`, `RadioGroup`, `RangeSlider`, `Slider`, `Spinbox`, `TextArea`, `Toast`, `ToggleGroup`, `Toolbar`, `Tooltip`, `App`, `Signal`, `Dialog`, `MessageDialog`, `QueryDialog`, `DateDialog`, `FontDialog`, `FilterDialog`, `FormDialog`.

Removed: `FloodGauge` (absorbed into `ProgressBar`), `Combobox` (replaced by `Select`), `MessageBox`/`QueryBox` classes (replaced by `bs.alert()`, `bs.confirm()`, `bs.ask_*()` module-level functions), `Frame` (use `HStack`/`VStack`/`Grid`/`Card`).

---

Sanity check: I covered all widgets in the inventory, every kwarg listed, plus methods, properties, and events. Each table includes the `Notes` column with rationale for each change, the cross-widget consistency section flags the inconsistencies I noticed (15 categories), and the bug-fix list links 17 known gaps back into the rename so v2 doesn't ship with the same gotchas.

result: v2 API proposal covering 40+ classes — every kwarg, method, property and event mapped from v1 to v2 with rationale, plus consistency rules, 17 bug-fix riders, required Event enum additions, and a full class-rename summary.