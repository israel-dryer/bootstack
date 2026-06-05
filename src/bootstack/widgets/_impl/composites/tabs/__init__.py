"""Tabs composite widget module."""

from .tabs import Tabs
from .tabview import TabView
from bootstack.events import (
    TabRef,
    TabChangeEvent,
    TabActivateEvent,
    TabDeactivateEvent,
    ChangeReason,
    ChangeMethod,
)

__all__ = [
    "Tabs",
    "TabView",
    "TabRef",
    "TabChangeEvent",
    "TabActivateEvent",
    "TabDeactivateEvent",
    "ChangeReason",
    "ChangeMethod",
]
