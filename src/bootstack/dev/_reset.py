"""Region teardown helpers for hot reload.

PROVISIONAL — part of the carved-out ``bootstack.dev`` surface.

Clearing a region destroys its child subtree (which fires ``<Destroy>`` on every
descendant — the same broadcast normal teardown uses, so per-widget
deregistration runs for free) and resets the layout engine's bookkeeping so the
freshly-built children grid cleanly.
"""
from __future__ import annotations

from typing import Any


def clear_container(container: Any) -> None:
    """Destroy everything a public container painted, leaving the frame reusable."""
    frame = _child_frame(container)
    if frame is None:
        return
    clear_frame(frame)


def clear_frame(frame: Any) -> None:
    """Destroy all children of a layout frame and reset its managed-child list."""
    try:
        children = list(frame.winfo_children())
    except Exception:
        return
    for child in children:
        try:
            child.destroy()
        except Exception:
            pass
    managed = getattr(frame, "_managed", None)
    if isinstance(managed, list):
        managed.clear()


def _child_frame(container: Any) -> Any:
    """The frame a container's children are actually placed in."""
    frame = getattr(container, "_flex_frame", None)
    if frame is not None:
        return frame
    getter = getattr(container, "_child_master", None)
    if callable(getter):
        try:
            return getter()
        except Exception:
            pass
    return getattr(container, "_internal", None)