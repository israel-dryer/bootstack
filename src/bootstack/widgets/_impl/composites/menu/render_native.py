"""macOS renderer — the native global menu bar.

Builds a flat `tk.Menu` cascade structure from a `MenuModel` and assigns it as
the window's menubar (`root['menu']`). On macOS this materializes as the native
global menu bar at the top of the screen.

Deliberately thin (this is why `MenuManager` is retired): single layer, **no
icons** (native Mac menus are text-only by convention), label translation for
semantic keys, and accelerator text for display. Actual key binding is owned by
`MenuModel.bind_shortcuts`, not the menu — `tk.Menu` accelerators never fire on
their own.
"""
from __future__ import annotations

import tkinter as tk
from typing import Any

from bootstack._runtime.shortcuts import tk_aqua_accelerator
from bootstack.widgets._impl.composites.menu.model import MenuItem, MenuModel


def _translate(text: str | None) -> str:
    """Resolve a semantic message key; pass plain text through unchanged."""
    if not text:
        return ""
    try:
        from bootstack.i18n import MessageCatalog

        return MessageCatalog.translate(text) or text
    except Exception:
        return text


class NativeMenuBar:
    """Native menubar (macOS) built from a `MenuModel` and attached to a window.

    Call `rebuild()` to re-render after the model changes; `destroy()` detaches
    the menubar from the window.
    """

    def __init__(self, root: Any, model: MenuModel) -> None:
        self._root = root
        self._model = model
        self._menubar: tk.Menu | None = None
        # Strong refs so Tk variables backing check/radio items aren't GC'd
        # while the menu holds them.
        self._var_refs: list[Any] = []
        self.rebuild()

    @property
    def model(self) -> MenuModel:
        """The menu model this menubar renders."""
        return self._model

    def set_model(self, model: MenuModel) -> None:
        """Swap in a new model and re-render."""
        self._model = model
        self.rebuild()

    def rebuild(self) -> None:
        """Rebuild the cascade structure and (re)attach it to the window."""
        menubar = tk.Menu(self._root, tearoff=0)
        self._var_refs = []
        radio_vars: dict[str, tk.StringVar] = {}

        for group in self._model:
            submenu = tk.Menu(menubar, tearoff=0)
            for item in group.items:
                self._add_item(submenu, item, radio_vars)
            menubar.add_cascade(label=_translate(group.text), menu=submenu)

        self._root["menu"] = menubar
        self._menubar = menubar

    def _add_item(
        self,
        submenu: tk.Menu,
        item: MenuItem,
        radio_vars: dict[str, tk.StringVar],
    ) -> None:
        if item.type == "separator":
            submenu.add_separator()
            return

        if item.type == "check":
            var = tk.BooleanVar(value=item.checked)
            self._var_refs.append(var)
            submenu.add_checkbutton(
                label=_translate(item.text),
                variable=var,
                command=item.on_click,
                state="disabled" if item.disabled else "normal",
            )
            return

        if item.type == "radio":
            var = radio_vars.setdefault(item.group or "", tk.StringVar())
            if var not in self._var_refs:
                self._var_refs.append(var)
            submenu.add_radiobutton(
                label=_translate(item.text),
                variable=var,
                value=item.value,
                command=item.on_click,
                state="disabled" if item.disabled else "normal",
            )
            return

        # action
        opts: dict[str, Any] = {
            "label": _translate(item.text),
            "command": item.on_click,
            "state": "disabled" if item.disabled else "normal",
        }
        # Native menus need the word-form accelerator (Tk renders the glyphs);
        # the pre-symbolized display would show the modifier but drop the key.
        acc = tk_aqua_accelerator(item.shortcut)
        if acc:
            opts["accelerator"] = acc
        submenu.add_command(**opts)

    def destroy(self) -> None:
        """Detach the menubar from the window and drop it."""
        try:
            self._root["menu"] = ""
        except Exception:
            pass
        if self._menubar is not None:
            try:
                self._menubar.destroy()
            except Exception:
                pass
        self._menubar = None
        self._var_refs = []