"""Step 8 — custom panel mode (escape hatch). One App/process.

`panel()` claims the workspace as a blank container the user fills, with no
provider cascade and no compaction; content is driven by hand via `content`.
"""

from __future__ import annotations

import pytest

from bootstack.widgets._impl.composites.shell import CustomProvider, Shell
from bootstack.widgets._impl.primitives.label import Label


def test_custom_panel_mode():
    shell = Shell(title="Custom")
    try:
        container = shell.panel()
        # Returns a usable container frame to fill directly.
        Label(container, text="Filters").pack()

        provider = shell.provider
        assert isinstance(provider, CustomProvider)
        assert provider.supports_compact is False
        assert provider.keys() == ()
        assert shell.workspace.supports_compact is False
        # Content region is exposed for hand-driven swapping.
        assert shell.workspace.content is not None

        # Ctrl-B can't compact a custom panel -> it hides.
        assert shell._can_compact_active() is False

        # The workspace already has a provider -> add_page is rejected.
        with pytest.raises(RuntimeError):
            shell.add_page("x")
    finally:
        shell.destroy()


def test_custom_provider_not_compactable():
    assert CustomProvider.supports_compact is False
