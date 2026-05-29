"""Tabs composite widget module."""

from .tabs import Tabs
from .tabview import TabView
from .events import (
    TabRef,
    TabChangeEventData,
    TabActivateEventData,
    TabDeactivateEventData,
    ChangeReason,
    ChangeMethod,
)

__all__ = [
    "Tabs",
    "TabView",
    "TabRef",
    "TabChangeEventData",
    "TabActivateEventData",
    "TabDeactivateEventData",
    "ChangeReason",
    "ChangeMethod",
]
