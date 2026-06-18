"""Context container for rendering a provider's content into a region frame.

A data-bound provider's `@detail` body is authored with public widgets
(`with bs.VStack(...): ...`), which parent to whatever container is on top of
the context stack. `ContentHost` wraps a plain region frame as such a container,
so the framework can push it, call the detail builder, and pop it — landing the
built widgets inside the content region.

Mirrors the public `_PageFrame` container protocol (`_child_master` /
`guide_layout`).
"""

from __future__ import annotations

from typing import Any

from bootstack.widgets._core.container import PACK_KEYS, normalize_fill
from bootstack.widgets._core.context import push_container, pop_container


class ContentHost:
    """A context-stack container that parents public widgets into `frame`."""

    def __init__(self, frame: Any) -> None:
        self._internal = frame

    def _child_master(self) -> Any:
        return self._internal

    def guide_layout(self, child: Any, **layout_kw: Any) -> None:
        # A content/sidebar region's top-level child should fill it — otherwise a
        # detail builder's container shrinks to its content and centers (looking
        # like huge padding). The flex placement kwargs (`grow` / `horizontal`)
        # don't apply to a plain region frame, so default to fill="both"/expand
        # and let any explicit pack option override.
        options: dict[str, Any] = {"fill": "both", "expand": True}
        if "fill" in layout_kw:
            options["fill"] = normalize_fill(layout_kw["fill"])
        options.update({k: v for k, v in layout_kw.items() if k in PACK_KEYS and k != "fill"})
        child._internal.pack(in_=self._internal, **options)

    def __enter__(self) -> "ContentHost":
        push_container(self)
        return self

    def __exit__(self, *exc: Any) -> None:
        pop_container(self)

    def clear(self) -> None:
        """Destroy all children currently in the frame."""
        for child in self._internal.winfo_children():
            child.destroy()
