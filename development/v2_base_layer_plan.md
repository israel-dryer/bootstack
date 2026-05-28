# bootstack v2 Public API — Base Layer Implementation Plan

**Audience:** Sonnet (executor). **Branch:** `feat/public-api-base` off `main`.

This plan covers the foundation of the v2 public API only — the context stack,
`PublicWidgetBase`, `Subscription`, `Event` enum, two-level event resolution,
and the container `guide_layout` protocol — plus three reference containers
(`HStack`, `VStack`, `Grid`), the new `App`, and one reference primitive
(`Button`) to prove the pattern end-to-end. Per-widget migration of the
remaining ~40 widgets is **out of scope**; that work follows this plan once
the foundation is in.

---

## 0. Architecture overview

### Composition, not inheritance

A public widget is a **plain Python object** that holds a reference to an
internal `tk`/`ttk` widget. It is **not** itself a `tk.Widget`. Reasons:

- The internal `.tk` attribute on every `tk.Widget` is the Tcl interpreter
  handle. Subclassing breaks the `.tk` escape-hatch property we want to expose.
- Users must never call `.pack()` / `.grid()` / `.bind()` on a public widget —
  composition makes that physically impossible (those methods don't exist on
  the Python object). The escape hatch is `widget.tk.pack(...)`,
  `widget.tk.bind(...)`, etc.
- Decouples the public surface from Tkinter's MRO and lets us swap internal
  implementations later without breaking the public API.

### Key relationships

```
PublicWidget                      (Python wrapper, not a tk.Widget)
  ._internal: tk.Widget | None    (the actual ttk/tk widget; set in __init__)
  .tk         → property over _internal (read-only)
  ._parent: PublicWidget | None   (the public parent that "owns" this widget)
```

Containers additionally expose:

```
PublicContainer(PublicWidget)
  ._child_master() → tk.Widget    # the tk parent for child._internal
  .guide_layout(child, **layout_kw) → None  # applies pack/grid/place
  __enter__/__exit__              # push/pop the context stack
```

For most containers, `._child_master()` returns `self._internal` itself. `App`
is the exception — it uses an internal content-frame so children don't pack
directly into the `tk.Tk` root.

### Layout flow on widget construction

```
1. user writes: bs.Label("hi", padding=4, fill="x")
2. Label.__init__ splits kwargs into (widget_kw, layout_kw)
3. Label.__init__ resolves parent: explicit parent= → context stack → None
4. Label.__init__ constructs internal:  self._internal = ttk.Label(parent._child_master(), **widget_kw)
5. Label.__init__ calls parent.guide_layout(self, **layout_kw)
6. guide_layout merges container defaults + per-child overrides
7. guide_layout calls self._internal.pack(...) (or .grid / .place)
```

### Out of scope for this plan

- Migration of any widget other than `Button` (used as a reference).
- Signal wiring details (`signal=` / `text_signal=`) inside widgets — covered
  generally but per-widget application happens later.
- Property setters for every kwarg — only the base machinery is built; widget
  authors add `@property` blocks during per-widget migration.
- `bs.attach()` escape hatch — listed but deferred until at least one widget
  needs it.
- `.tk` on `Signal` (rename from `.var`) — already exists, separate one-line
  change; flagged in Phase A but not part of the base layer plan proper.

---

## 1. File locations

Create a new package: **`src/bootstack/widgets/v2/`**. All public layer code
lives here during development. Once v1 is removed, the user can rename to drop
`v2/`. Internals (`bootstack/widgets/primitives/*`, `bootstack/widgets/composites/*`)
are unchanged.

Tree to create:

```
src/bootstack/widgets/v2/
├── __init__.py                # re-exports the public symbols
├── base.py                    # PublicWidgetBase
├── container.py               # PublicContainer mixin + LAYOUT_KEYS sets
├── context.py                 # thread-local context stack
├── events.py                  # Event namespace + event maps
├── subscription.py            # Subscription class
├── exceptions.py              # UnknownEventError + base v2 exceptions
├── stacks.py                  # HStack, VStack
├── grid.py                    # Grid (the public container, not the layout manager)
├── app.py                     # public App wrapper
└── primitives/
    ├── __init__.py
    └── button.py              # reference Button implementation
```

`bootstack/__init__.py` is **not** changed by this plan. The v2 symbols are
accessible via `from bootstack.widgets.v2 import App, HStack, VStack, Grid, Button`
during development; the lazy-import wiring of `bs.*` gets updated when v2
replaces v1 (later PR).

---

## Phase A — Foundations (no inter-dependencies; can be implemented in parallel)

### A1. `events.py` — Event namespace and global map

Create `src/bootstack/widgets/v2/events.py`.

```python
from __future__ import annotations
from enum import Enum


class _EventCategory(str, Enum):
    """String-valued enum so members compare equal to plain strings."""
    pass


class _Widget(_EventCategory):
    CLICK         = "click"
    DOUBLE_CLICK  = "double_click"
    RIGHT_CLICK   = "right_click"
    HOVER         = "hover"
    LEAVE         = "leave"
    FOCUS         = "focus"
    BLUR          = "blur"
    RESIZE        = "resize"
    EXPAND        = "expand"
    COLLAPSE      = "collapse"
    ACTIVATE      = "activate"
    DEACTIVATE    = "deactivate"
    DISMISS       = "dismiss"


class _Input(_EventCategory):
    CHANGE   = "change"
    INPUT    = "input"
    SUBMIT   = "submit"
    VALIDATE = "validate"
    VALID    = "valid"
    INVALID  = "invalid"
    COMMIT   = "commit"


class _Selection(_EventCategory):
    SELECT   = "select"
    DESELECT = "deselect"


class _App(_EventCategory):
    THEME_CHANGE      = "theme_change"
    PAGE_MOUNT        = "page_mount"
    PAGE_UNMOUNT      = "page_unmount"
    PAGE_WILL_MOUNT   = "page_will_mount"
    PAGE_CHANGE       = "page_change"


class Event:
    """Namespace of v2 event constants.

    Members compare equal to their string values, so
    `widget.on("click", h)` and `widget.on(Event.Widget.CLICK, h)` are
    interchangeable.
    """
    Widget    = _Widget
    Input     = _Input
    Selection = _Selection
    App       = _App


# Two-level event lookup
# Level 1: widget-class-specific overrides (resolved against type(public_widget).__mro__)
# Level 2: global fallback
GLOBAL_EVENT_MAP: dict[str, str] = {
    # Widget
    "click":        "<Button-1>",
    "double_click": "<Double-Button-1>",
    "right_click":  "<Button-3>",
    "hover":        "<Enter>",
    "leave":        "<Leave>",
    "focus":        "<FocusIn>",
    "blur":         "<FocusOut>",
    "resize":       "<Configure>",
    # Input — keystrokes
    "input":        "<KeyRelease>",
    "submit":       "<Return>",
    # App-level Tk-virtual events
    "theme_change": "<<ThemeChanged>>",
}

# Per-class override map.
# Populated by widgets during their __init__ via `register_widget_events`.
# Keyed by the public widget class (not instance).
_CLASS_EVENT_MAPS: dict[type, dict[str, str]] = {}


def register_widget_events(cls: type, mapping: dict[str, str]) -> None:
    """Attach a class-specific event map to a public widget class.

    Each entry maps the v2 name (e.g. "select") to the Tk sequence
    (e.g. "<<TreeviewSelect>>"). Class maps take precedence over the
    global map during resolution.
    """
    _CLASS_EVENT_MAPS[cls] = mapping


def resolve_event(public_widget, name: str) -> str:
    """Resolve a v2 event name to a Tk sequence.

    Lookup order:
        1. Walk the public widget's MRO; first class-specific match wins.
        2. Global map.
        3. Pass through literal `<...>` or `<<...>>` strings unchanged.
        4. Raise UnknownEventError.
    """
    from bootstack.widgets.v2.exceptions import UnknownEventError

    # Pass-through for literal Tk sequences
    if name.startswith("<") and name.endswith(">"):
        return name

    for klass in type(public_widget).__mro__:
        cmap = _CLASS_EVENT_MAPS.get(klass)
        if cmap and name in cmap:
            return cmap[name]

    if name in GLOBAL_EVENT_MAP:
        return GLOBAL_EVENT_MAP[name]

    raise UnknownEventError(
        f"Unknown event {name!r} on {type(public_widget).__name__}. "
        f"Known events: {sorted(set(GLOBAL_EVENT_MAP) | set().union(*(m for m in _CLASS_EVENT_MAPS.values())))}"
    )
```

**Notes for Sonnet:**
- `_EventCategory(str, Enum)` so members are usable as strings.
- The global map only contains true cross-widget events. Widget-specific
  virtuals like `<<TreeviewSelect>>`, `<<TabChanged>>`, `<<Change>>`, etc.
  are added during per-widget migration via `register_widget_events`.
- Don't add `Input.CHANGE`, `Input.VALIDATE`, `Selection.SELECT`, etc.
  to `GLOBAL_EVENT_MAP` — these are widget-specific Tk virtual events.
  They go in per-widget maps.

### A2. `exceptions.py`

```python
class BootstackV2Error(Exception):
    """Base class for all v2 public API errors."""


class UnknownEventError(BootstackV2Error):
    """Raised by `widget.on(name, ...)` when `name` cannot be resolved."""


class ParentResolutionError(BootstackV2Error):
    """Raised when a widget cannot resolve its parent (no context, no parent= kwarg, no root)."""
```

### A3. `subscription.py`

```python
from __future__ import annotations
import tkinter
from typing import Callable


class Subscription:
    """Handle returned by `widget.on(...)`. Cancels the binding when `.cancel()`
    is called or the context manager exits.

    Idempotent: calling `cancel()` more than once is a no-op.
    """

    __slots__ = ("_widget", "_sequence", "_bind_id", "_cancelled")

    def __init__(self, widget: tkinter.Misc, sequence: str, bind_id: str):
        self._widget = widget
        self._sequence = sequence
        self._bind_id = bind_id
        self._cancelled = False

    def cancel(self) -> None:
        if self._cancelled:
            return
        self._cancelled = True
        try:
            self._widget.unbind(self._sequence, self._bind_id)
        except tkinter.TclError:
            # Widget may already be destroyed; ignore.
            pass

    def __enter__(self) -> "Subscription":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.cancel()

    @property
    def cancelled(self) -> bool:
        return self._cancelled
```

**Notes:**
- The `widget` here is the **internal** `tk.Widget` — that's what owns the
  bind ID. `Subscription` does not need to know about the public wrapper.
- `Signal.subscribe()` returns a Tk trace ID, not a `Subscription`. A
  follow-up PR adapts `Signal` to return `Subscription`-compatible handles;
  out of scope for this plan.

### A4. `context.py` — thread-local container stack

```python
from __future__ import annotations
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bootstack.widgets.v2.container import PublicContainer

_local = threading.local()


def _stack() -> list:
    s = getattr(_local, "stack", None)
    if s is None:
        s = []
        _local.stack = s
    return s


def push_container(container: "PublicContainer") -> None:
    _stack().append(container)


def pop_container(expected: "PublicContainer") -> None:
    s = _stack()
    if not s or s[-1] is not expected:
        # Either empty or out of order — both are programmer errors.
        # Be defensive: pop only if the expected container is on the stack.
        if expected in s:
            s.remove(expected)
        return
    s.pop()


def current_container() -> "PublicContainer | None":
    s = _stack()
    return s[-1] if s else None
```

**Notes:**
- Thread-local rather than module-global so multi-threaded test runners and
  any pathological user code don't cross-contaminate.
- `pop_container(expected)` is forgiving: if `__exit__` fires out of order
  (e.g. because of an exception during widget creation), we don't corrupt
  the stack. The mismatched-pop branch is reachable in error paths.

### A5. `container.py` — layout key sets only (other contents land in Phase C)

For Phase A, define just the constants:

```python
from __future__ import annotations

# Module-level frozensets so membership checks are O(1).
# Sourced from tkinter.Pack.pack / tkinter.Grid.grid / tkinter.Place.place options.
PACK_KEYS = frozenset({
    "side", "fill", "expand", "anchor",
    "padx", "pady", "ipadx", "ipady",
    "before", "after", "in_",
})

GRID_KEYS = frozenset({
    "row", "column", "rowspan", "columnspan",
    "sticky", "padx", "pady", "ipadx", "ipady",
    "in_",
})

PLACE_KEYS = frozenset({
    "x", "y", "relx", "rely",
    "width", "height", "relwidth", "relheight",
    "anchor", "bordermode", "in_",
})

# Keys that signal "user wants absolute positioning"
PLACE_TRIGGER_KEYS = frozenset({"x", "y", "relx", "rely", "relwidth", "relheight"})

# Place's `width`, `height`, `anchor` collide with widget-level options.
# For Phase A/B/C, we ignore these collisions and treat them as widget kwargs
# unless one of PLACE_TRIGGER_KEYS is present. This decision is documented in
# CLAUDE.md ("PLACE_KEYS will need care... deferred until public property
# names are settled per-widget"). Sonnet should NOT try to fully resolve the
# collision in this plan.
```

### A6. (Flagged, deferred) Rename `Signal.var` → `Signal.tk`

Already noted in `v2_api_proposal.md`. Add `tk` as a property aliasing `var`;
keep `var` as a deprecated alias for one release. This is a single edit in
`src/bootstack/signals/signal.py` — Sonnet should batch this into Phase A as
a tiny side-quest:

```python
@property
def tk(self) -> tk.Variable:
    return self._var

# Keep `var` for now; do not delete in this PR.
```

---

## Phase B — `PublicWidgetBase` (depends on A1–A5)

### B1. `base.py`

```python
from __future__ import annotations

import tkinter
from typing import Any, Callable

from bootstack.widgets.v2.context import current_container
from bootstack.widgets.v2.container import PACK_KEYS, GRID_KEYS, PLACE_KEYS, PLACE_TRIGGER_KEYS
from bootstack.widgets.v2.events import resolve_event
from bootstack.widgets.v2.subscription import Subscription
from bootstack.widgets.v2.exceptions import ParentResolutionError


class PublicWidgetBase:
    """Base class for every public v2 widget.

    Subclasses MUST:
      - Set `self._internal` (an internal tk/ttk widget) before calling
        `_attach_to_parent`.
      - Pass `master=parent._child_master()` to the internal widget's
        constructor.

    Subclasses SHOULD:
      - Use `_split_layout_kwargs(kwargs)` to extract layout options from
        their constructor kwargs.
      - Call `_attach_to_parent(layout_kw)` after constructing `_internal`.
    """

    # Subclasses override if they need to suppress automatic placement
    # (e.g. dialogs, toplevels, tooltips).
    _auto_place: bool = True

    # Set during __init__
    _internal: tkinter.Misc
    _parent: "PublicWidgetBase | None"

    # ----- Parent resolution -----

    @staticmethod
    def _resolve_parent(explicit_parent: "PublicWidgetBase | None") -> "PublicWidgetBase | None":
        """Resolve the public parent.

        Order:
            1. Explicit `parent=` kwarg
            2. Current container on the context stack
            3. None (the caller will use the root window directly)
        """
        if explicit_parent is not None:
            return explicit_parent
        return current_container()

    # ----- Layout kwarg extraction -----

    @staticmethod
    def _split_layout_kwargs(kwargs: dict) -> dict:
        """Pop layout kwargs out of `kwargs` and return them as a new dict.

        Mutates `kwargs` in place. The widget keeps whatever remains.

        Layout-key resolution:
            - If any PLACE_TRIGGER_KEYS is present, treat all PLACE_KEYS as
              layout. (Phase-A note: `width`/`height`/`anchor` collisions are
              left alone; they stay in `kwargs` as widget options. The trigger
              keys themselves never collide.)
            - Else, treat the union of PACK_KEYS and GRID_KEYS as layout.
              Per-container `guide_layout` decides which subset is applicable.
        """
        place_mode = any(k in kwargs for k in PLACE_TRIGGER_KEYS)
        if place_mode:
            layout_keys = PLACE_KEYS - {"width", "height", "anchor"}
            layout_keys = layout_keys | PLACE_TRIGGER_KEYS
        else:
            layout_keys = PACK_KEYS | GRID_KEYS
            # `padx`/`pady`/`ipadx`/`ipady` are layout for both pack and grid.
            # `padding` on a widget is INSIDE the widget — stays in kwargs.

        return {k: kwargs.pop(k) for k in list(kwargs) if k in layout_keys}

    # ----- Attachment -----

    def _attach_to_parent(self, layout_kw: dict) -> None:
        """Place `self._internal` under `self._parent` using parent's guide_layout.

        Called once at the end of the subclass __init__, after `_internal` and
        `_parent` are set. No-op when `_auto_place` is False.
        """
        if not self._auto_place:
            return
        parent = self._parent
        if parent is None:
            # No parent — caller intends to place the widget manually via
            # widget.tk.pack(...), or this is a top-level App.
            return
        # parent should be a PublicContainer; ducktyped check
        guide = getattr(parent, "guide_layout", None)
        if guide is None:
            raise ParentResolutionError(
                f"{type(parent).__name__} is not a container (no guide_layout); "
                f"cannot place {type(self).__name__} inside it. "
                f"Wrap children in HStack/VStack/Grid/Card, or pass parent=<container>."
            )
        guide(self, **layout_kw)

    # ----- Public `.tk` escape hatch -----

    @property
    def tk(self) -> tkinter.Misc:
        """Underlying tk/ttk widget. UNSUPPORTED — for escape-hatch use only."""
        return self._internal

    # ----- Events -----

    def on(self, event: str, handler: Callable[[tkinter.Event], Any]) -> Subscription:
        """Bind `handler` to `event` and return a `Subscription`."""
        sequence = resolve_event(self, str(event))
        bind_id = self._internal.bind(sequence, handler, add="+")
        return Subscription(self._internal, sequence, bind_id)

    def emit(self, event: str, *, data: dict | None = None) -> None:
        """Synthesize and fire `event` on the underlying widget."""
        sequence = resolve_event(self, str(event))
        # Tk's event_generate accepts only string/numeric kwargs; we attach
        # the payload via a private attribute the handler can read off the
        # event object if needed.
        if data is not None:
            self._internal._bs_emit_data = data  # type: ignore[attr-defined]
        try:
            self._internal.event_generate(sequence)
        finally:
            if data is not None:
                try:
                    delattr(self._internal, "_bs_emit_data")
                except AttributeError:
                    pass

    # Subclasses generated by per-widget code add typed `on_<name>` shorthands
    # that delegate to `self.on(name, handler)`. The base class doesn't define
    # them — they're per-widget.

    # ----- Repr -----

    def __repr__(self) -> str:
        try:
            name = self._internal._w  # type: ignore[attr-defined]
        except AttributeError:
            name = "?"
        return f"<{type(self).__name__} {name}>"
```

**Design notes for Sonnet:**

- The constructor pattern for every public widget will follow this shape
  (illustrated in Phase F with `Button`):

  ```python
  def __init__(self, label="", *, parent=None, **kwargs):
      self._parent = self._resolve_parent(parent)
      layout_kw = self._split_layout_kwargs(kwargs)
      tk_master = self._parent._child_master() if self._parent else None
      self._internal = _InternalButton(tk_master, text=label, **kwargs)
      self._attach_to_parent(layout_kw)
  ```

- `__init__` order is **critical**: parent resolution → split layout kwargs →
  construct internal → attach. Splitting must happen before internal
  construction so layout kwargs don't leak into the internal ttk constructor.

- The base class does **not** know about Signals. Per-widget code wires
  `signal=` / `text_signal=` to the internal widget. This plan doesn't
  prescribe that wiring.

- Subclasses overriding `__init__` MUST call no `super().__init__()` — there
  is no Python super to call. The base class provides static helpers
  (`_resolve_parent`, `_split_layout_kwargs`, `_attach_to_parent`) and
  instance helpers (`tk`, `on`, `emit`).

---

## Phase C — Container protocol (depends on B)

### C1. Extend `container.py` with `PublicContainer`

```python
from __future__ import annotations

import tkinter
from typing import Any

from bootstack.widgets.v2.base import PublicWidgetBase
from bootstack.widgets.v2.context import push_container, pop_container
from bootstack.widgets.v2.container import (
    PACK_KEYS, GRID_KEYS, PLACE_KEYS, PLACE_TRIGGER_KEYS,
)


class PublicContainer(PublicWidgetBase):
    """Mixin/base for public containers (HStack, VStack, Grid, Card, App).

    Subclasses MUST implement:
      - `_child_master(self) -> tk.Widget`: returns the tk widget that
        children's `_internal` should be parented to.
      - `_default_layout_method(self) -> "pack" | "grid"`: which manager
        this container uses by default.
      - `_merge_layout_options(self, child, layout_kw) -> (method, options)`:
        merge container defaults with per-child overrides.
    """

    # ----- Container API -----

    def _child_master(self) -> tkinter.Misc:
        """Default: children are parented directly to `self._internal`."""
        return self._internal

    def _default_layout_method(self) -> str:
        raise NotImplementedError

    def _merge_layout_options(
        self, child: PublicWidgetBase, layout_kw: dict
    ) -> tuple[str, dict]:
        raise NotImplementedError

    # ----- The protocol PublicWidgetBase._attach_to_parent calls -----

    def guide_layout(self, child: PublicWidgetBase, **layout_kw: Any) -> None:
        """Place `child._internal` under this container.

        Method selection:
            1. If any PLACE_TRIGGER_KEYS is present, use `place()`.
            2. Else use the container's default (`pack` or `grid`).
        """
        place_mode = any(k in layout_kw for k in PLACE_TRIGGER_KEYS)
        tk_widget = child._internal

        if place_mode:
            options = {k: v for k, v in layout_kw.items() if k in PLACE_KEYS}
            tk_widget.place(in_=self._child_master(), **options)
            return

        method, options = self._merge_layout_options(child, layout_kw)
        if method == "pack":
            tk_widget.pack(in_=self._child_master(), **options)
        elif method == "grid":
            tk_widget.grid(in_=self._child_master(), **options)
        else:
            raise ValueError(f"Unknown layout method: {method!r}")

    # ----- Context manager -----

    def __enter__(self) -> "PublicContainer":
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pop_container(self)
        # Do not suppress exceptions.
        return None
```

**Notes:**
- Per-widget code (e.g. `Card`) will multiply-inherit `PublicContainer` for
  the protocol methods. Composite containers can override `_child_master` to
  return a non-self tk widget (used by `App`).
- `place()` is exposed only via the inline-kwarg mechanism, never via a
  separate public method — matches the settled design.

---

## Phase D — `HStack`, `VStack`, `Grid` (depends on C)

### D1. `stacks.py` — `HStack` and `VStack`

Both wrap the existing internal `bootstack.widgets.primitives.packframe.PackFrame`
as their `_internal`. Container defaults map to `PackFrame`'s ctor kwargs.

```python
from __future__ import annotations

from typing import Any

from bootstack.widgets.primitives.packframe import PackFrame
from bootstack.widgets.v2.container import PublicContainer


class _StackBase(PublicContainer):
    _direction: str  # set by subclass

    def __init__(
        self,
        *,
        parent=None,
        # Self-placement (consumed by parent.guide_layout)
        fill: str | None = None,
        expand: bool | None = None,
        anchor: str | None = None,
        # Child-guidance (this container's defaults for its children)
        gap: int = 0,
        padding: Any = None,
        fill_items: str | None = None,
        expand_items: bool | None = None,
        anchor_items: str | None = None,
        # ttk.Frame styling
        accent: str | None = None,
        variant: str | None = None,
        surface: str | None = None,
        show_border: bool = False,
        width: int | None = None,
        height: int | None = None,
        # Any extra layout kwargs to forward to parent's guide_layout
        **extra_layout_kw: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        # Combine the explicit self-placement kwargs with anything else
        # the caller passed (e.g. row=, column= for grid placement).
        layout_kw = {k: v for k, v in {
            "fill": fill, "expand": expand, "anchor": anchor,
        }.items() if v is not None}
        layout_kw.update(self._split_layout_kwargs(extra_layout_kw))
        if extra_layout_kw:
            # Unknown kwargs that weren't layout — pass to PackFrame as
            # styling, or raise. For now, fold into the frame constructor.
            pass

        # Child-guidance defaults persisted on the container
        self._gap = gap
        self._fill_items = fill_items
        self._expand_items = expand_items
        self._anchor_items = anchor_items

        # Build PackFrame kwargs
        frame_kwargs: dict[str, Any] = {
            "direction": self._direction,
            "gap": gap,
            "fill_items": fill_items,
            "expand_items": expand_items,
            "anchor_items": anchor_items,
        }
        if padding is not None:
            frame_kwargs["padding"] = padding
        if accent is not None:
            frame_kwargs["accent"] = accent
        if variant is not None:
            frame_kwargs["variant"] = variant
        if surface is not None:
            frame_kwargs["surface"] = surface
        if show_border:
            frame_kwargs["show_border"] = show_border
        if width is not None:
            frame_kwargs["width"] = width
        if height is not None:
            frame_kwargs["height"] = height
        frame_kwargs.update(extra_layout_kw)  # any leftovers

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = PackFrame(tk_master, **frame_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- PublicContainer protocol -----

    def _default_layout_method(self) -> str:
        return "pack"

    def _merge_layout_options(self, child, layout_kw):
        # PackFrame's own _on_child_pack already does the merging — but we
        # bypass it: PackFrame's hooks are invoked when a child *itself*
        # calls .pack(). Here, the public layer calls .pack() with merged
        # options directly, so PackFrame's _on_child_pack will still fire.
        # That's fine — the hook tracks `_managed`, which is what we want
        # for repacking when child-guidance defaults change.
        # We pass through only PACK_KEYS, dropping anything Pack doesn't know.
        from bootstack.widgets.v2.container import PACK_KEYS
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        return ("pack", options)


class HStack(_StackBase):
    _direction = "horizontal"


class VStack(_StackBase):
    _direction = "vertical"
```

**Notes for Sonnet:**
- PackFrame already implements `_on_child_pack` which applies the
  direction/gap/fill_items/expand_items/anchor_items defaults. That means
  calling `child.pack(**options)` is enough — PackFrame intercepts and
  layers its container defaults on top. The public layer should pass only
  the **per-child overrides** (the kwargs the user explicitly set on the
  child), and let PackFrame do the merge.
- Verify by reading `packframe.py:173` (`_on_child_pack`) — it accepts the
  user options dict and calls `_build_options(index, user_options)` which
  layers defaults beneath. The implementation is correct as-is for v2.
- **Test:** after implementation, place three labels in an HStack and verify
  they appear horizontally with the configured `gap`.

### D2. `grid.py` — `Grid` (public container)

Wraps `bootstack.widgets.primitives.gridframe.GridFrame`. Same pattern as
the stacks; child overrides include `row`, `column`, `rowspan`, `columnspan`,
`sticky`.

```python
from __future__ import annotations

from typing import Any

from bootstack.widgets.primitives.gridframe import GridFrame
from bootstack.widgets.v2.container import PublicContainer, GRID_KEYS


class Grid(PublicContainer):
    def __init__(
        self,
        *,
        parent=None,
        rows: int | list | None = None,
        columns: int | list | None = None,
        gap: int | tuple[int, int] = 0,
        sticky_items: str | None = None,
        auto_flow: str = "row",
        padding: Any = None,
        accent: str | None = None,
        variant: str | None = None,
        surface: str | None = None,
        show_border: bool = False,
        width: int | None = None,
        height: int | None = None,
        # Self-placement
        fill: str | None = None,
        expand: bool | None = None,
        anchor: str | None = None,
        **extra_layout_kw: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = {k: v for k, v in {
            "fill": fill, "expand": expand, "anchor": anchor,
        }.items() if v is not None}
        layout_kw.update(self._split_layout_kwargs(extra_layout_kw))

        frame_kwargs: dict[str, Any] = {
            "rows": rows,
            "columns": columns,
            "gap": gap,
            "sticky_items": sticky_items,
            "auto_flow": auto_flow,
        }
        for k, v in {
            "padding": padding, "accent": accent, "variant": variant,
            "surface": surface, "show_border": show_border,
            "width": width, "height": height,
        }.items():
            if v not in (None, False):
                frame_kwargs[k] = v

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = GridFrame(tk_master, **frame_kwargs)
        self._attach_to_parent(layout_kw)

    def _default_layout_method(self) -> str:
        return "grid"

    def _merge_layout_options(self, child, layout_kw):
        options = {k: v for k, v in layout_kw.items() if k in GRID_KEYS}
        return ("grid", options)
```

`Card` is **out of scope** for this plan — it's a thin wrapper choice over
HStack/VStack/Grid and is added during per-widget migration.

---

## Phase E — `App` (depends on D)

### E1. `app.py`

`App` is the root container. It does not have a parent; calling
`._attach_to_parent` is a no-op (the bound `_parent` is `None`). Internally
it owns:

- `self._tk_root`: a `bootstack._runtime.app.App` (the existing internal
  `tk.Tk` subclass — unchanged).
- `self._content_frame`: a `PackFrame` whose `master` is `self._tk_root`,
  expanding to fill the root. **This is what children pack into.**

```python
from __future__ import annotations

from typing import Any

from bootstack._runtime.app import App as _InternalApp
from bootstack.widgets.primitives.packframe import PackFrame
from bootstack.widgets.v2.container import PublicContainer


class App(PublicContainer):
    """The application window. Behaves as an implicit VStack from the user's
    perspective: accepts `padding`, `gap`, `fill_items`, `expand_items`,
    `anchor_items` and applies them to its internal content frame.

    `app.tk` returns the underlying `tk.Tk` root window.
    """

    _auto_place = False  # no parent

    def __init__(
        self,
        *,
        title: str | None = None,
        size: tuple[int, int] | None = None,
        settings: Any = None,
        localize: Any = None,
        # Child-guidance (apply to content frame)
        padding: Any = None,
        gap: int = 0,
        fill_items: str | None = None,
        expand_items: bool | None = None,
        anchor_items: str | None = None,
        # Frame styling for content
        surface: str | None = None,
        # Misc App kwargs forwarded to internal App
        **app_kwargs: Any,
    ) -> None:
        self._parent = None  # App has no parent

        # Internal Tk root — uses existing _runtime.app.App
        self._tk_root = _InternalApp(
            title=title,
            size=size,
            settings=settings,
            localize=localize,
            **app_kwargs,
        )

        # The user-facing "this widget" for App.tk is the Tk root.
        # The internal content frame is what children pack INTO.
        frame_kwargs: dict[str, Any] = {
            "direction": "vertical",
            "gap": gap,
            "fill_items": fill_items,
            "expand_items": expand_items,
            "anchor_items": anchor_items,
        }
        if padding is not None:
            frame_kwargs["padding"] = padding
        if surface is not None:
            frame_kwargs["surface"] = surface

        self._content_frame = PackFrame(self._tk_root, **frame_kwargs)
        # Fill the root window with the content frame
        self._content_frame.pack(fill="both", expand=True)

        # PublicWidgetBase contract: `_internal` is the widget you bind events
        # to / pass as a tk.Misc reference. For App, that's the root.
        self._internal = self._tk_root

    # ----- PublicContainer overrides -----

    def _child_master(self):
        """Children pack into the content frame, NOT the Tk root."""
        return self._content_frame

    def _default_layout_method(self) -> str:
        return "pack"

    def _merge_layout_options(self, child, layout_kw):
        from bootstack.widgets.v2.container import PACK_KEYS
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        return ("pack", options)

    # ----- App lifecycle -----

    def run(self) -> None:
        """Show the window and start the event loop."""
        self._tk_root.deiconify()
        self._tk_root.mainloop()

    # Alias matching v1
    mainloop = run

    # ----- Context manager: also un-withdraws the root on exit -----

    def __exit__(self, exc_type, exc, tb) -> None:
        super().__exit__(exc_type, exc, tb)
        # Settled design: App hides root on enter, shows on exit (eliminates
        # FOUC). The internal `_runtime.app.App` already calls `self.withdraw()`
        # in __init__. Only App.__exit__ runs update_idletasks (per CLAUDE.md).
        try:
            self._tk_root.update_idletasks()
        except Exception:
            pass
        return None
```

**Notes for Sonnet:**

- `_runtime.app.App.__init__` already calls `self.withdraw()`. App.run() (or
  the implicit `mainloop` on `__exit__` + caller invocation) calls
  `deiconify()` and `mainloop()`. The "hide on enter, show on exit" pattern
  works because the internal App is already withdrawn from construction.
- Don't call `mainloop()` inside `__exit__`. The `with` block is for child
  registration; `app.run()` (called after the block) starts the loop.

  ```python
  with bs.App(title="Demo") as app:
      bs.Label("Hello")
  app.run()
  ```

- Add `App` to `bootstack/widgets/v2/__init__.py` exports.

---

## Phase F — Reference primitive: `Button` (depends on B)

### F1. `primitives/button.py`

The reference widget — proves the base layer works end-to-end. Wraps the
existing internal `bootstack.widgets.primitives.button.Button` as `_internal`.

```python
from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets.primitives.button import Button as _InternalButton
from bootstack.widgets.v2.base import PublicWidgetBase
from bootstack.widgets.v2.events import register_widget_events


class Button(PublicWidgetBase):
    """A clickable action trigger.

    Args:
        label: Button label text (positional or via kwarg).
        on_click: Callback fired when the button is clicked.
        accent: Accent token, e.g. 'primary', 'danger'.
        variant: Style variant, e.g. 'solid', 'outline'.
        icon: Bootstrap Icons name.
        disabled: If True, button is non-interactive.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        label: str = "",
        *,
        on_click: Callable[[], Any] | None = None,
        accent: str | None = None,
        variant: str | None = None,
        icon: str | None = None,
        icon_only: bool = False,
        disabled: bool = False,
        parent: PublicWidgetBase | None = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {"text": label}
        if on_click is not None:
            internal_kwargs["command"] = on_click
        if accent is not None:
            internal_kwargs["accent"] = accent
        if variant is not None:
            internal_kwargs["variant"] = variant
        if icon is not None:
            internal_kwargs["icon"] = icon
        if icon_only:
            internal_kwargs["icon_only"] = True
        if disabled:
            internal_kwargs["state"] = "disabled"
        internal_kwargs.update(kwargs)  # anything not split as layout

        self._internal = _InternalButton(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def label(self) -> str:
        return str(self._internal.cget("text"))

    @label.setter
    def label(self, value: str) -> None:
        self._internal.configure(text=value)

    @property
    def disabled(self) -> bool:
        return str(self._internal.cget("state")) == "disabled"

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._internal.configure(state="disabled" if value else "normal")

    # ----- Methods -----

    def click(self) -> None:
        """Programmatically fire the button's command."""
        self._internal.invoke()

    # ----- Shorthand event helpers -----

    def on_click(self, handler):  # type: ignore[no-redef]
        # Allow both ctor kwarg (on_click=fn) and method (.on_click(fn))
        # by checking arity. Simpler: the ctor uses internal Button's `command=`;
        # this method registers an *additional* click handler via `<Button-1>`.
        return self.on("click", lambda e: handler())


# Register Button's class-specific events (none beyond the global map — but
# this is where TreeView, Tabs, Form, etc. will hook their virtual events
# during per-widget migration.)
register_widget_events(Button, {})
```

**Note on the `on_click` collision:**
- `on_click=` is a constructor kwarg; `.on_click(handler)` is a runtime method.
- The setter inside `__init__` uses the internal Button's `command=` (so it
  fires regardless of focus state).
- The instance method uses an event binding so the user can attach multiple
  handlers. This is a documented dual API per the v2 proposal.
- Subscribers added via `.on_click(handler)` use `<Button-1>` (the global
  `click` mapping). That's a real click, not a synthetic invoke.

---

## Phase G — Smoke tests

Create `tests/widgets/v2/test_base_layer.py`:

### G1. Context stack test

```python
def test_context_stack_isolated_per_thread():
    # push/pop from main thread; spawn thread; verify thread sees empty stack.
```

### G2. Layout kwarg split test

```python
def test_split_layout_kwargs_pack_grid():
    kw = {"fill": "x", "expand": True, "padding": 4, "text": "hi"}
    layout = PublicWidgetBase._split_layout_kwargs(kw)
    assert layout == {"fill": "x", "expand": True}
    assert kw == {"padding": 4, "text": "hi"}  # padding stays — it's widget option
```

### G3. Subscription cancel test

```python
def test_subscription_cancels_handler():
    # Bind <Button-1>, fire event_generate, verify handler ran.
    # Cancel subscription, fire event_generate, verify handler did NOT run.
```

### G4. Event resolution test

```python
def test_resolve_event_global():
    # "click" → "<Button-1>"

def test_resolve_event_unknown_raises():
    # "nonsense" → UnknownEventError

def test_resolve_event_passthrough():
    # "<<MyVirtual>>" → "<<MyVirtual>>"
```

### G5. End-to-end placement test (integration, requires a Tk root)

```python
def test_label_button_inside_hstack():
    with App(title="Test") as app:
        with HStack(gap=8) as row:
            b1 = Button("A")
            b2 = Button("B")
    # Both buttons should be packed into row._content_frame (== row._internal)
    assert b1._internal.master is row._internal
    assert b2._internal.master is row._internal
    # And row should be packed into app._content_frame
    assert row._internal.master is app._content_frame
```

### G6. Explicit parent= override test

```python
def test_explicit_parent_overrides_context_stack():
    with App() as app:
        with VStack() as outer:
            with HStack() as inner:
                # Parented explicitly to outer, not inner
                lbl = Label("hi", parent=outer)
    assert lbl._internal.master is outer._internal
```

(Skip G5/G6 in CI if no display; gate behind a `@pytest.mark.gui` marker.)

---

## Dependencies and recommended implementation order

```
A1 events.py              ──┐
A2 exceptions.py          ──┤
A3 subscription.py        ──┤
A4 context.py             ──┼──> B base.py ──> C container.py ──> D stacks/grid ──> E app.py
A5 container.py (sets)    ──┘                                                          │
                                                                                       └─> F button.py
                                                                                       │
                                                                                       └─> G tests
```

Phase A modules have **no inter-dependencies** and can be implemented in any
order or in parallel. Phase B depends on all of A. Phase C extends Phase A's
`container.py` (which is why the layout-key constants live there from the
start). Phases D, E, F all depend on C. Tests (G) come last.

---

## Acceptance criteria for this PR

1. `python -c "from bootstack.widgets.v2 import App, HStack, VStack, Grid, Button"` succeeds.
2. The G5 integration test passes (manual run is fine if CI has no display).
3. The following demo script runs and shows a window with two buttons side
   by side, the second one printing "B clicked" on click:

   ```python
   from bootstack.widgets.v2 import App, HStack, Button

   with App(title="v2 demo", size=(300, 100), padding=16, gap=8) as app:
       with HStack(gap=8):
           Button("A")
           Button("B", on_click=lambda: print("B clicked"))
   app.run()
   ```

4. `Button("X").tk` returns a `ttk.Button` instance.
5. `sub = btn.on("click", h); sub.cancel()` unbinds the handler.
6. `btn.on("nonsense", h)` raises `UnknownEventError`.
7. No changes to `bootstack/widgets/primitives/*` or `bootstack/_runtime/*`
   are required (or made). Only the `Signal.tk` property addition (Phase A6)
   touches existing code.

---

## What this plan deliberately defers

- Per-widget migration (Label, Switch, Entry → TextField, etc.).
- `bs.attach()` free function.
- Card public container.
- `signal=` / `text_signal=` kwarg wiring inside widgets (the mechanism is
  here; the per-widget application is per-widget work).
- `Signal.subscribe()` returning `Subscription` instead of a trace ID.
- Property layer — only Button has `label`/`disabled` properties as a
  reference. Other widgets get theirs during migration.
- `bs.alert()`, `bs.confirm()`, `bs.ask_*()` module-level functions.
- `place()` collision resolution for `width`/`height`/`anchor` (deferred per
  CLAUDE.md).
- The `Event.App.PAGE_*` events — `App` doesn't fire any in this PR. They
  exist in the enum for future PageStack migration.

These are tracked as follow-up PRs once this base layer is in.