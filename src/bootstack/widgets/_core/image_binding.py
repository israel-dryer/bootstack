"""Bind a public image handle onto an internal widget.

The `image=` slot on text widgets accepts a public `bootstack.images.Image`
handle. Because a handle holds no display resource until it is used, this helper
renders it against the target widget and, when the handle follows the theme (a
token-colored icon), re-renders it whenever the theme changes — releasing the
binding when the widget is destroyed.
"""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bootstack.images import Image


def bind_image(public_widget, internal_widget, image: "Image") -> None:
    """Render `image` onto `internal_widget`, following the theme if needed.

    Args:
        public_widget: The public wrapper; strong references to the handle and
            its rendered image are stored on it so they are not collected.
        internal_widget: The underlying widget to display the image on.
        image: The image handle to render and bind.
    """
    # Calling this again on the same widget (a live `image=` update) must not
    # stack theme bindings — release any prior one first.
    _release_theme_binding(public_widget)

    photo = image._materialize(internal_widget)
    internal_widget.configure(image=photo)
    public_widget._image_handle = image
    public_widget._image_photo = photo

    if not image._is_theme_following:
        return

    root = internal_widget.winfo_toplevel()

    def _reapply(_event=None) -> None:
        try:
            image._invalidate()
            new_photo = image._materialize(internal_widget)
            internal_widget.configure(image=new_photo)
            public_widget._image_photo = new_photo
        except tk.TclError:
            pass

    bind_id = root.bind("<<BsThemeChanged>>", _reapply, add="+")
    public_widget._image_theme_binding = (root, bind_id)

    def _release(event) -> None:
        if event.widget is not internal_widget:
            return
        _release_theme_binding(public_widget)

    internal_widget.bind("<Destroy>", _release, add="+")


def _release_theme_binding(public_widget) -> None:
    """Unbind a previously installed `<<BsThemeChanged>>` handler, if any."""
    prev = getattr(public_widget, "_image_theme_binding", None)
    if prev is None:
        return
    root, bind_id = prev
    try:
        root.unbind("<<BsThemeChanged>>", bind_id)
    except tk.TclError:
        pass
    public_widget._image_theme_binding = None


def resolve_window_icon(icon):
    """Normalize a window `icon=` argument to `(path, deferred_image)`.

    Exactly one of the returned values is non-`None` (or both are, for `None`
    input). A `path` can be handed to the window at construction; a deferred
    image must be rendered and applied after the window's root exists.

    Args:
        icon: An icon file path, an `Image` handle, or an `AppIcon`.
    """
    if icon is None:
        return None, None
    from bootstack.images import AppIcon, Image

    if isinstance(icon, AppIcon):
        return icon._icon_path(), None
    if isinstance(icon, Image):
        return None, icon
    return str(icon), None
