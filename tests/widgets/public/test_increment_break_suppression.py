"""Regression tests for `<<Increment>>` suppression on a disabled field (#401).

`NumberEntryPart._handle_increment_event` / `_handle_decrement_event` returned
`'break'` when the field was not interactive. Before #392 the runtime wrote its
own binding script for virtual events and discarded handler return values, so
that was inert. The #392 fix emits the toolkit's stock script shape, in which
`'break'` means *stop the remaining handlers for this event* — so dispatching
`<<Increment>>` on a disabled or read-only field silently aborted the rest of
that dispatch, including any `on_increment` subscriber.

The guard is about not stepping the value. Speaking for every other handler was
never the intent, and is not something the framework should inherit from the
toolkit; suppression, if ever wanted, needs a designed API.
"""
from __future__ import annotations

import bootstack as bs


def test_disabled_number_field_does_not_suppress_later_increment_handlers(app):
    field = bs.NumberField(value=1, disabled=True)
    part = field._internal._entry
    later = []
    part.bind("<<Increment>>", lambda e: later.append(1), add="+")
    app._tk_root.update_idletasks()

    part.event_generate("<<Increment>>")
    app._tk_root.update()

    assert later == [1]


def test_disabled_number_field_still_refuses_to_step(app):
    """The guard's actual purpose must survive the fix."""
    field = bs.NumberField(value=1, disabled=True)
    part = field._internal._entry
    before = field.value
    app._tk_root.update_idletasks()

    part.event_generate("<<Increment>>")
    app._tk_root.update()

    assert field.value == before
