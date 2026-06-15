"""Icon mixin for widgets that support theme-aware icons.

Provides a `@configure_delegate('icon')` handler that applies an icon through
the style system and preserves current style tokens, orientation, and
surface color where applicable.
"""

from __future__ import annotations

from typing import Any, Callable

from bootstack.widgets._impl.mixins.configure_mixin import configure_delegate


class IconMixin:
    """Adds `icon` configuration support via the style engine."""

    configure_style_options: Callable
    rebuild_style: Callable

    @configure_delegate("icon")
    def _delegate_icon(self, value: Any = None) -> Any:
        """Get or set the widget icon.

        Args:
            value: Icon name (str), icon spec dict, or None to query the
                current value.

        Returns:
            Current icon value when querying (``value`` is None), otherwise
            the result of rebuilding the widget style.
        """
        if value is None:
            return self.configure_style_options("icon")
        else:
            self.configure_style_options(icon=value)
            return self.rebuild_style()

    @configure_delegate("icon_only")
    def _delegate_icon_only(self, value: Any = None) -> Any:
        """Get or set icon-only display mode.

        When ``True``, removes the extra padding reserved for text so the
        icon fills the available space without a label gap.

        Args:
            value: ``True`` to enable icon-only mode, ``False`` to disable,
                or None to query the current value.

        Returns:
            Current ``icon_only`` value when querying, otherwise the result
            of rebuilding the widget style.
        """
        if value is None:
            return self.configure_style_options("icon_only")
        else:
            self.configure_style_options(icon_only=value)
            return self.rebuild_style()


__all__ = ["IconMixin"]
