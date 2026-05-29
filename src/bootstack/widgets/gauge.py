from __future__ import annotations

from typing import Any

from bootstack.widgets._impl.composites.meter import Meter as _InternalMeter
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.events import register_widget_events


class Gauge(PublicWidgetBase):
    """A circular gauge for displaying a value within a range.

    Args:
        value: Initial value.
        min_value: Minimum of the range. Default `0`.
        max_value: Maximum of the range. Default `100`.
        subtitle: Text displayed below the value.
        value_prefix: Text prepended to the value display (e.g. `'$'`).
        value_suffix: Text appended to the value display (e.g. `'%'`).
        value_format: Format string for the value (e.g. `'{:.1f}'`).
        size: Diameter in pixels. Default `200`.
        thickness: Arc width in pixels. Default `10`.
        meter_type: `'full'` (default) for a full circle or `'semi'` for a semicircle.
        segment_width: Segment width for a dashed/segmented arc. `0` means solid.
        interactive: If True, the user can click/drag to change the value.
        step: Increment used in interactive mode.
        show_text: If False, hides the value text.
        accent: Accent token for the arc colour.
        parent: Override the context-stack parent.
    """

    def __init__(
        self,
        value: int | float = 0,
        *,
        min_value: int | float = 0,
        max_value: int | float = 100,
        subtitle: str | None = None,
        value_prefix: str | None = None,
        value_suffix: str | None = None,
        value_format: str = "{:.0f}",
        size: int = 200,
        thickness: int = 10,
        meter_type: str = "full",
        segment_width: int = 0,
        interactive: bool = False,
        step: int | float = 1,
        show_text: bool = True,
        accent: str | None = None,
        parent: Any = None,
        **kwargs: Any,
    ) -> None:
        self._parent = self._resolve_parent(parent)
        layout_kw = self._split_layout_kwargs(kwargs)

        tk_master = self._parent._child_master() if self._parent else None

        internal_kwargs: dict[str, Any] = {
            "value": value,
            "minvalue": min_value,
            "maxvalue": max_value,
            "value_format": value_format,
            "size": size,
            "thickness": thickness,
            "meter_type": meter_type,
            "segment_width": segment_width,
            "interactive": interactive,
            "step_size": step,
            "show_text": show_text,
        }
        if subtitle is not None:
            internal_kwargs["subtitle"] = subtitle
        if value_prefix is not None:
            internal_kwargs["value_prefix"] = value_prefix
        if value_suffix is not None:
            internal_kwargs["value_suffix"] = value_suffix
        if accent is not None:
            internal_kwargs["accent"] = accent
        internal_kwargs.update(kwargs)

        self._internal = _InternalMeter(tk_master, **internal_kwargs)
        self._attach_to_parent(layout_kw)

    # ----- Properties -----

    @property
    def value(self) -> int | float:
        return self._internal.value

    @value.setter
    def value(self, v: int | float) -> None:
        self._internal.value = v

    @property
    def subtitle(self) -> str:
        return self._internal.subtitle

    @subtitle.setter
    def subtitle(self, v: str) -> None:
        self._internal.subtitle = v


register_widget_events(Gauge, {})
