"""Reactive signal primitives for bootstack widgets."""
from .signal import Signal

__all__ = [
    "Signal",
]

# TraceOperation is an internal low-level type for variable-trace callbacks
# (no public Signal method exposes it). Import it from `bootstack.signals.types`
# if internal code needs it.
