"""Typed event payloads for TabView."""
from __future__ import annotations

from typing import Literal
from typing_extensions import TypedDict

ChangeReason = Literal["user", "api", "hide", "forget", "unknown"]
ChangeMethod = Literal["click", "key", "programmatic", "unknown"]


class TabRef(TypedDict):
    """Identifies a tab by key and display text."""
    key: str
    text: str


class TabChangeEventData(TypedDict):
    """Payload for ``on_tab_changed`` / ``<<TabChanged>>``."""
    current: TabRef
    previous: TabRef | None
    reason: ChangeReason
    via: ChangeMethod


class TabActivateEventData(TypedDict):
    """Payload for ``on_tab_activated`` / ``<<TabActivate>>``."""
    key: str
    text: str


class TabDeactivateEventData(TypedDict):
    """Payload for ``on_tab_deactivated`` / ``<<TabDeactivate>>``."""
    key: str
    text: str
