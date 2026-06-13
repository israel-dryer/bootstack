"""Smoke test for the data-bound list_nav provider + @detail (step 5).

Verifies: records populate the sidebar, the detail builder receives the public
record dict, the first record auto-selects once detail is set, selection
re-renders the detail, and add_page after list_nav is rejected. One App/process.
"""

from __future__ import annotations

import bootstack as bs
from bootstack.data import MemoryDataSource
from bootstack.widgets._impl.composites.shell import Shell


def test_list_nav_master_detail_cascade():
    shell = Shell(title="ListNav")
    try:
        source = MemoryDataSource().load([
            {"text": "Spectrometer", "icon": "cpu", "status": "active"},
            {"text": "Thermocouple", "icon": "thermometer", "status": "idle"},
        ])

        shell.list_nav(source=source)

        seen: list[dict] = []

        @shell.detail
        def render(record):
            seen.append(record)
            bs.Label(record["text"])          # parents into the content region

        # Detail registration auto-selects the first record.
        assert seen, "detail should render the first record on registration"
        first = seen[0]
        assert first["text"] == "Spectrometer"
        assert "id" in first                  # normalized public record dict
        assert shell.content.winfo_children(), "detail body should be mounted"

        # Selecting another record re-renders the detail.
        keys = shell.provider.keys()
        assert len(keys) == 2
        shell._on_nav_select(keys[1])
        assert seen[-1]["text"] == "Thermocouple"
        sel_id = seen[-1]["id"]               # real record id (for source ops)

        # --- Live source refresh (changes are coalesced via after_idle) ---
        seen.clear()

        # Insert: a new record appears in the sidebar.
        new_id = source.insert({"text": "DAQ-9211", "icon": "hdd", "status": "active"})
        shell.update()                        # flush the coalesced change
        assert str(new_id) in shell.provider.keys()
        assert len(shell.provider.keys()) == 3

        # Update the SELECTED record -> its detail re-renders with fresh data.
        source.update(sel_id, {"text": "Thermocouple", "icon": "thermometer", "status": "offline"})
        shell.update()
        assert seen and seen[-1]["status"] == "offline"

        # Delete the selected record -> selection reconciles to the first item.
        source.delete(sel_id)
        shell.update()
        assert str(sel_id) not in shell.provider.keys()
        assert shell.current_page in shell.provider.keys()

        # Mutual exclusivity: add_page after list_nav is rejected.
        import pytest
        with pytest.raises(RuntimeError):
            shell.add_page("home", text="Home")
    finally:
        shell.destroy()
