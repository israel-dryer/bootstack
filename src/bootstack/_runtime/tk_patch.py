"""Install-time patching for Tk widgets only.

This module applies bootstack's Tk autostyle behavior to Tk widgets by
wrapping their constructors. It does not affect ttk widgets, which are
provided as explicit subclasses in the bootstack.widgets package.
"""

from __future__ import annotations

import tkinter as tk

from bootstack.style.bootstyle import Bootstyle

# Native Tk widget classes whose constructors get the autostyle wrapper.
# Limited to the raw Tk widgets the framework actually instantiates or
# subclasses (everything else is built on ttk). Implementation detail of this
# patch — intentionally not exported anywhere.
_TK_WIDGETS = (
    tk.Tk,        # application root window
    tk.Toplevel,  # secondary windows, dialogs, popups
    tk.Frame,     # Slider/RangeSlider/multiline-text container subclasses
    tk.Text,      # TextArea / CodeEditor cores
    tk.Canvas,    # sliders, scroll view, gauge drawing
    tk.Menu,      # context menus and menu bars
)


def install_tk_autostyle() -> None:
    """Patch Tk widgets to enable autostyle via Bootstyle.

    - Wraps Tk widget `__init__` with surface color inheritance and theme
      background application using registered Tk builders.
    - Leaves ttk widgets untouched; ttk integration is done via wrappers.
    """
    # Ensure Tk builders are registered
    import bootstack.style.builders_tk  # noqa: F401

    for widget in _TK_WIDGETS:
        _init = Bootstyle.override_tk_widget_constructor(widget.__init__)
        widget.__init__ = _init


__all__ = ["install_tk_autostyle"]
