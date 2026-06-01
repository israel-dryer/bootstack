from __future__ import annotations

from typing import Any

from bootstack.widgets._impl.primitives.packframe import PackFrame
from bootstack.widgets._core.container import PublicContainer, PACK_KEYS, normalize_fill
from bootstack.widgets.types import AccentToken, SurfaceToken, Fill, Anchor


class _StackBase(PublicContainer):
    _direction: str  # set by subclass

    def __init__(
        self,
        *,
        parent: Any = None,
        # Self-placement
        fill: Fill | str | None = None,
        expand: bool | None = None,
        anchor: Anchor | str | None = None,
        # Child-guidance defaults
        gap: int = 0,
        padding: Any = None,
        fill_items: Fill | str | None = None,
        expand_items: bool | None = None,
        anchor_items: Anchor | str | None = None,
        # Frame styling
        accent: AccentToken | str | None = None,
        surface: SurfaceToken | str | None = None,
        show_border: bool = False,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        """Create the stack container.

        Args:
            fill: Fill direction of this stack within its parent. One of
                ``'x'``, ``'y'``, ``'both'``, or ``'none'``. Defaults to
                ``None`` (no fill).
            expand: Whether this stack expands to consume extra space in the
                parent container. Defaults to ``None``.
            anchor: Placement anchor of this stack within its parent slot.
                Standard Tkinter anchor strings: ``'n'``, ``'s'``, ``'e'``,
                ``'w'``, ``'center'``, etc.
            gap: Spacing in pixels between child widgets. Defaults to ``0``.
            padding: Space in pixels between the stack border and its
                content. Accepts an integer (all sides) or a 2-tuple
                ``(x, y)``. Defaults to ``None`` (no padding).
            fill_items: Default ``fill`` direction applied to every child.
                One of ``'x'``, ``'y'``, ``'both'``, or ``'none'``.
                Individual children can override this with their own
                ``fill=``.
            expand_items: When ``True``, each child expands to consume extra
                space along the stack direction. Defaults to ``None``.
            anchor_items: Default alignment anchor for children that do not
                fill their slot. Standard Tkinter anchor strings: ``'n'``,
                ``'s'``, ``'e'``, ``'w'``, ``'center'``, etc.
            accent: Color intent token applied to the stack background. One
                of ``'primary'``, ``'secondary'``, ``'info'``, ``'success'``,
                ``'warning'``, ``'danger'``, ``'muted'``, ``'default'``.
                Defaults to ``None`` (inherits from parent surface).
            surface: Background surface token. One of ``'content'``,
                ``'card'``, ``'chrome'``, ``'overlay'``. Overrides the
                automatic surface inherited from the parent. Defaults to
                ``None``.
            show_border: When ``True``, draws a 1 px border around the
                stack frame. Defaults to ``False``.
            width: Fixed width of the stack in pixels. Disables frame
                propagation so children cannot resize the container.
                Setting both ``width=`` and ``height=`` fully constrains
                the frame with no extra kwargs needed. When only
                ``width=`` is set, height collapses to zero — add
                ``fill='y'`` and ``expand=True`` to let the parent
                control it. Defaults to ``None`` (size from children).
            height: Fixed height of the stack in pixels. Disables frame
                propagation so children cannot resize the container.
                Setting both ``height=`` and ``width=`` fully constrains
                the frame with no extra kwargs needed. When only
                ``height=`` is set, width collapses to zero — add
                ``fill='x'`` and ``expand=True`` to let the parent
                control it. Defaults to ``None`` (size from children).
            parent: Override the context-stack parent widget.
        """
        self._parent = self._resolve_parent(parent)

        layout_kw: dict[str, Any] = {}
        if fill is not None:
            layout_kw["fill"] = normalize_fill(fill)
        if expand is not None:
            layout_kw["expand"] = expand
        if anchor is not None:
            layout_kw["anchor"] = anchor

        frame_kwargs: dict[str, Any] = {
            "direction": self._direction,
            "gap": gap,
            "fill_items": normalize_fill(fill_items),
            "expand_items": expand_items,
            "anchor_items": anchor_items,
        }
        if padding is not None:
            frame_kwargs["padding"] = padding
        if accent is not None:
            frame_kwargs["accent"] = accent
        if surface is not None:
            frame_kwargs["surface"] = surface
        if show_border:
            frame_kwargs["show_border"] = show_border
        if width is not None:
            frame_kwargs["width"] = width
        if height is not None:
            frame_kwargs["height"] = height
        if width is not None or height is not None:
            frame_kwargs["propagate"] = False

        self._fill_items = normalize_fill(fill_items)
        self._expand_items = expand_items
        self._anchor_items = anchor_items

        tk_master = self._parent._child_master() if self._parent else None
        self._internal = PackFrame(tk_master, **frame_kwargs)
        self._attach_to_parent(layout_kw)

    def _default_layout_method(self) -> str:
        return "pack"

    def _merge_layout_options(self, child: Any, layout_kw: dict) -> tuple[str, dict]:
        options = {k: v for k, v in layout_kw.items() if k in PACK_KEYS}
        if "fill" not in options and self._fill_items:
            options["fill"] = self._fill_items
        if "expand" not in options and self._expand_items is not None:
            options["expand"] = self._expand_items
        if "anchor" not in options and self._anchor_items:
            options["anchor"] = self._anchor_items
        return ("pack", options)


class HStack(_StackBase):
    """Horizontal stack — lays out children left-to-right with optional gap and alignment.

    A lightweight container that packs children side by side using the pack
    geometry manager. Use ``gap=`` to space children evenly, ``anchor_items=``
    to align them vertically, and ``fill_items=`` to stretch them along the
    horizontal axis.

    Example::

        with bs.HStack(gap=8, anchor_items="center"):
            bs.Label("Name:")
            bs.TextField()
    """
    _direction = "horizontal"


class VStack(_StackBase):
    """Vertical stack — lays out children top-to-bottom with optional gap and alignment.

    A lightweight container that packs children one above the other using the
    pack geometry manager. Use ``gap=`` to space children evenly,
    ``fill_items='x'`` to stretch them to the full width, and ``expand=True``
    to let the stack grow vertically in its parent.

    Example::

        with bs.VStack(gap=12, fill_items="x", padding=16):
            bs.Label("Title", font="heading-md[bold]")
            bs.TextField()
            bs.Button("Submit", accent="primary")
    """
    _direction = "vertical"