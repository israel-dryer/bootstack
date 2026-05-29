"""Decoration-set diff engine.

Per-layer state stored as a dict keyed by (start_tk, end_tk, style).
Diff is a dict comparison: O(|symmetric difference|) Tk tag calls.
"""
from __future__ import annotations

import tkinter as tk
from typing import Sequence, TYPE_CHECKING

from bootstack.widgets._impl.composites.textarea.decoration import (
    LineDecoration, RangeDecoration,
)

if TYPE_CHECKING:
    from bootstack.widgets._impl.composites.textarea.core import _MultilineCore
    from bootstack.widgets._impl.composites.textarea.style_registry import StyleRegistry

# Key: (start_tk_index, end_tk_index, style_name)
_LayerState = dict[tuple[str, str, str], dict | None]


class DecorationDiff:
    """Applies decoration sets to a Text widget using a diff-based approach.

    Maintains per-layer state so that only changed decorations cause Tk
    tag_add / tag_remove calls. For a 200-decoration viewport with one
    edited token, this is ~2 Tk calls instead of clearing and rebuilding.
    """

    def __init__(self, core: _MultilineCore, style_registry: StyleRegistry) -> None:
        self._core = core
        self._text = core.text
        self._styles = style_registry
        # layer -> current decoration state
        self._layers: dict[str, _LayerState] = {}
        # layer -> priority (lower = below)
        self._priorities: dict[str, int] = {}

    def register_layer(self, name: str, priority: int = 0) -> None:
        """Register a decoration layer.

        Args:
            name: Layer identifier (used in style tag names).
            priority: Tag raise order — higher priority layers appear on top.
        """
        if name not in self._layers:
            self._layers[name] = {}
            self._priorities[name] = priority

    def set_decorations(
        self,
        layer: str,
        decorations: Sequence[RangeDecoration | LineDecoration],
    ) -> None:
        """Apply a new decoration set to *layer*, diffing against the previous set.

        Args:
            layer: The layer to update.
            decorations: New complete set of decorations for this layer.
        """
        if layer not in self._layers:
            self.register_layer(layer)

        new_state = _build_state(decorations)
        old_state = self._layers[layer]

        old_keys = set(old_state.keys())
        new_keys = set(new_state.keys())

        removed = old_keys - new_keys
        added = new_keys - old_keys

        for start, end, style in removed:
            tag = self._styles.tag_name(layer, style)
            try:
                self._text.tag_remove(tag, start, end)
            except tk.TclError:
                pass

        for start, end, style in added:
            tag = self._styles.tag_name(layer, style)
            if not self._styles.is_configured(layer, style):
                self._styles.configure_tag(layer, style)
            try:
                self._text.tag_add(tag, start, end)
            except tk.TclError:
                pass

        self._layers[layer] = new_state
        self._raise_layers()

    def clear_layer(self, layer: str) -> None:
        """Remove all decorations from *layer*."""
        self.set_decorations(layer, [])

    def _raise_layers(self) -> None:
        """Enforce layer priority order via tag_raise."""
        ordered = sorted(self._priorities.items(), key=lambda x: x[1])
        for layer, _ in ordered:
            state = self._layers.get(layer, {})
            seen_tags: set[str] = set()
            for _, _, style in state:
                tag = self._styles.tag_name(layer, style)
                if tag not in seen_tags:
                    seen_tags.add(tag)
                    try:
                        self._text.tag_raise(tag)
                    except tk.TclError:
                        pass


def _build_state(
    decorations: Sequence[RangeDecoration | LineDecoration],
) -> _LayerState:
    """Convert a list of decorations to the internal dict-key format."""
    state: _LayerState = {}
    for dec in decorations:
        if isinstance(dec, RangeDecoration):
            key = (dec.start.to_tk(), dec.end.to_tk(), dec.style)
            state[key] = dec.meta
        elif isinstance(dec, LineDecoration):
            start = f"{dec.line}.0"
            end = f"{dec.line}.end"
            key = (start, end, dec.style)
            state[key] = dec.meta
    return state
