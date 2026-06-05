"""Deferred and repeating task scheduling tied to a widget's lifetime.

Every public widget exposes a ``Schedule`` via its ``schedule`` property; each
scheduling call returns a cancellable ``Job``.
"""
from bootstack.scheduling._schedule import Job, Schedule

__all__ = [
    "Job",
    "Schedule",
]
