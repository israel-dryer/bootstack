"""Reusable `icon` / `image` property mixins for widgets that accept them.

Widgets in the button family take a widget-level `icon=` (a Bootstrap icon name)
and/or `image=` (an `Image` handle) at construction. These mixins expose those as
live, settable properties so they can be changed after construction — `image`
updates in place (no rebuild, no flicker).
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from bootstack.widgets.types import IconSpec


class IconProperty:
    """Adds a live `icon` property to a widget whose internal accepts `icon=`."""

    @property
    def icon(self) -> "str | IconSpec | None":
        """The icon shown on the widget, or `None` if none is set.

        A Bootstrap Icons name, or an `IconSpec` mapping (`{'name', 'size',
        'color'}`) for control over size and color.
        """
        return self._internal.configure_style_options("icon")

    @icon.setter
    def icon(self, value: "str | IconSpec | None") -> None:
        self._internal.configure(icon=value)


class ImageProperty:
    """Adds a live `image` property to a widget whose internal accepts `image=`."""

    @property
    def image(self) -> Any:
        """The displayed image handle, or `None`.

        Assigning an `Image` (from `bootstack.images`) updates the picture in
        place — no rebuild — which avoids the flicker of recreating the widget.
        """
        return getattr(self, "_image_handle", None)

    @image.setter
    def image(self, value: Any) -> None:
        from bootstack.widgets._core.image_binding import (
            _release_theme_binding,
            bind_image,
        )

        if value is None:
            # Drop any theme-following binding from a previous Image, otherwise it
            # keeps re-applying a now-removed image on theme changes (and pins it).
            _release_theme_binding(self)
            self._internal.configure(image="")
            self._image_handle = None
            self._image_photo = None
            return
        from bootstack.images import Image as _ImageHandle

        if isinstance(value, _ImageHandle):
            bind_image(self, self._internal, value)
        else:
            _release_theme_binding(self)
            self._internal.configure(image=value)
            self._image_handle = None
            self._image_photo = value


__all__ = ["IconProperty", "ImageProperty"]
