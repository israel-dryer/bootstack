"""Regression tests for `Form.set()` partial-update semantics (#387).

`set()` iterated *every* field and applied `self._data.get(key)`, which is
`None` for keys absent from the passed mapping. Those writes were discarded
only because setting `None` was itself a no-op — so partial updates appeared
to work by accident. Repairing the `None` no-op without this change would have
turned every partial `form.set()` into a destructive full-form overwrite.

`set()` now writes only the keys it is given and merges them into the form
data instead of replacing it.
"""
from __future__ import annotations

from datetime import date

import bootstack as bs


def _form(app):
    form = bs.Form(items=[
        bs.FieldItem(key="name", label="Name"),
        bs.FieldItem(key="city", label="City"),
        bs.FieldItem(key="d", label="D", editor="datefield"),
    ])
    app._tk_root.update_idletasks()
    form.set({"name": "Bob", "city": "Denver", "d": date(2024, 1, 1)})
    return form


def test_partial_set_leaves_other_fields_untouched(app):
    form = _form(app)

    form.set({"d": date(2030, 6, 6)})

    data = form.get()
    assert data["name"] == "Bob"
    assert data["city"] == "Denver"
    assert data["d"] == date(2030, 6, 6)


def test_partial_set_can_still_clear_the_key_it_names(app):
    # Omitting a key must not clear it, but naming it with None must.
    form = _form(app)

    form.set({"d": None})

    data = form.get()
    assert data["d"] is None
    assert data["name"] == "Bob"


def test_partial_set_merges_into_form_data(app):
    # `_data` was replaced wholesale, so a partial update dropped the keys it
    # did not mention; only re-reading the widgets papered over it.
    form = _form(app)

    form.set({"name": "Ada"})

    assert form.data["city"] == "Denver"
    assert form.data["name"] == "Ada"


def test_unknown_keys_are_ignored_for_field_writes(app):
    # A whole record from a data source may carry columns the form does not
    # show; bulk writes stay tolerant (targeted `set_field_value` still raises).
    form = _form(app)

    form.set({"name": "Ada", "id": 17, "created_at": "2026-01-01"})

    assert form.get()["name"] == "Ada"


def test_unknown_keys_round_trip_through_the_form_data(app):
    # Extra columns are carried, not dropped, so a record can be read back and
    # saved with its identity intact.
    form = _form(app)

    form.set({"name": "Ada", "id": 17})

    assert form.get()["id"] == 17


def test_setting_every_key_still_replaces_all(app):
    form = _form(app)

    form.set({"name": "", "city": "", "d": None})

    data = form.get()
    assert data["d"] is None
    assert not data["name"]
    assert not data["city"]
