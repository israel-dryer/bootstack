"""ChangeNotifier filter — fires <<Change>> after every edit."""
from __future__ import annotations

from typing import TYPE_CHECKING
from bootstack.widgets.composites.textarea.filter import EditFilter

if TYPE_CHECKING:
    from bootstack.widgets.composites.textarea.core import _MultilineCore


class ChangeNotifier(EditFilter):
    """Fires `<<Change>>` on the core's Text widget after every edit.

    The event payload (`event.data`) is a dict with keys:
    - `op`: `"insert"` or `"delete"`
    - `index`: The position where the edit occurred (Tk index string).
    """

    def __init__(self) -> None:
        super().__init__()
        self._core: _MultilineCore | None = None

    def attach(self, core: _MultilineCore) -> None:
        self._core = core

    def detach(self, core: _MultilineCore) -> None:
        self._core = None

    def insert(self, index: str, chars: str, tags=None) -> None:
        self.delegate.insert(index, chars, tags)
        self._notify("insert", index)

    def delete(self, index1: str, index2: str | None = None) -> None:
        self.delegate.delete(index1, index2)
        self._notify("delete", index1)

    def _notify(self, op: str, index: str) -> None:
        if self._core is not None:
            try:
                self._core.text.event_generate(
                    "<<Change>>",
                    data={"op": op, "index": index},
                    when="tail",
                )
            except Exception:
                pass
