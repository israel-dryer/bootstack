"""bootstack — a full UI framework for Python desktop apps built on Tkinter.

All widgets, dialogs, style utilities, and application primitives are
accessible directly from this namespace via lazy imports.

Examples:
    ```python
    import bootstack as bs

    app = bs.App(title="My App", themename="bootstrap-light")
    bs.Label(app, text="Hello, world!").pack(padx=20, pady=20)
    app.mainloop()
    ```
"""
import importlib as _importlib
from importlib.metadata import version as _pkg_version
from typing import TYPE_CHECKING

__version__ = _pkg_version("bootstack")

from tkinter import (
    BooleanVar,
    Canvas as _tkCanvas,
    DoubleVar,
    Frame as _tkFrame,
    IntVar,
    Menu as _tkMenu,
    PhotoImage,
    StringVar,
    Text as _tkText,
    Tk as _tkTk,
    Variable,
)

# Re-export tk widgets with original names before importing submodules
Tk = _tkTk
Menu = _tkMenu
Text = _tkText
Canvas = _tkCanvas
TkFrame = _tkFrame  # Exported as TkFrame to avoid conflict with bs.Frame
# Eagerly import BootstrapIcon to prevent circular import during style bootstrapping
from ttkbootstrap_icons_bs import BootstrapIcon  # noqa: E402

# Constants are available via bootstack.constants module
# (see constants.py which re-exports from core.constants)

if TYPE_CHECKING:
    from bootstack.widgets.types import (
        BaseWidgetKwargs, StyledKwargs,
        Anchor, BorderMode, CompoundMode, Direction,
        Fill, Justify, Orient, Relief, Side, Sticky,
        WidgetState, WidgetDensity,
        AccentToken, VariantToken, SurfaceToken,
    )
    from bootstack._runtime.app import App, AppSettings, Window, get_app_settings, get_current_app
    from bootstack._runtime.toplevel import Toplevel
    from bootstack._runtime.menu import MenuManager, create_menu, create_menu_items
    from bootstack._runtime.shortcuts import Shortcuts, Shortcut, get_shortcuts
    from bootstack.widgets.composites.appshell import AppShell
    from bootstack.widgets.composites.compositeframe import CompositeFrame, CompositeFrameKwargs
    from bootstack.widgets.composites.list.listitem import ListItemKwargs
    from bootstack.style import (
        Font, Style, Typography,
        get_style, get_style_builder, get_theme, get_theme_provider,
        set_theme, toggle_theme, get_theme_color, get_themes, register_user_theme,
    )
    from bootstack.widgets import (
        Accordion, Badge, Button, ButtonGroup, Calendar, Card,
        CheckButton, CheckToggle, Combobox, ContextMenu, ContextMenuItem,
        DateEntry, DropdownButton, Entry, Expander, Field, FieldOptions,
        FloodGauge, Form, Frame, GridFrame, Label, LabelFrame,
        LabeledScale, ListItem, ListView, MenuBar, MenuButton, Meter,
        Notebook, NumericEntry, OptionMenu, PackFrame, PanedWindow,
        PageStack, PasswordEntry, PathEntry, Progressbar, RadioButton,
        RadioGroup, RadioToggle, Scale, Scrollbar,
        TextArea, TextAreaInputEventData, TextAreaValidationEventData,
        CodeEditor, EditFilter,
        ScrollView, SelectBox, Separator, SideNav, SideNavItem,
        SideNavGroup, SideNavHeader, SideNavSeparator, SizeGrip, Spinbox,
        SpinnerEntry, Switch, TableView, TextEntry, TimeEntry, Toast,
        TabItem, Tabs, TabView,
        TabRef, TabChangeEventData, TabActivateEventData, TabDeactivateEventData,
        ChangeReason, ChangeMethod,
        ToggleGroup, Toolbar, ToolTip, TreeView, TK_WIDGETS, TTK_WIDGETS,
    )
    from bootstack.dialogs import (
        Dialog, DialogButton, FilterDialog, FormDialog,
        MessageDialog, MessageBox, QueryDialog, QueryBox,
        DateDialog, FontDialog, ColorChooser, ColorChooserDialog, ColorDropperDialog,
    )
    from bootstack.data import (
        BaseDataSource, MemoryDataSource, SqliteDataSource,
        FileDataSource, FileSourceConfig, DataSourceProtocol, Record, Primitive,
    )
    from bootstack.i18n import MessageCatalog, L, LV, IntlFormatter
    from bootstack._core.images import Image
    from ttkbootstrap_icons_bs import BootstrapIcon
    from bootstack.signals import Signal, TraceOperation
    from bootstack.validation import ValidationRule, ValidationResult
    from bootstack._core.variables import SetVar


_TK_EXPORTS = [
    "Tk",
    "Menu",
    "Text",
    "Canvas",
    "TkFrame",
    "Variable",
    "StringVar",
    "IntVar",
    "BooleanVar",
    "DoubleVar",
    "PhotoImage",
]

# Single source of truth: module-to-exports mapping
# Organized by category for clarity
_TTK_PRIMITIVES = [
    "Button", "CheckButton", "Combobox", "Entry", "Frame", "Label",
    "LabelFrame", "MenuButton", "Notebook", "OptionMenu", "PanedWindow",
    "Progressbar", "RadioButton", "Scale", "Scrollbar", "Separator",
    "SizeGrip", "Spinbox", "TreeView",
]

_MODULE_EXPORTS = {
    # Widget type aliases and base TypedDicts
    "bootstack.widgets.types": [
        "BaseWidgetKwargs", "StyledKwargs",
        "Anchor", "BorderMode", "CompoundMode", "Direction",
        "Fill", "Justify", "Orient", "Relief", "Side", "Sticky",
        "WidgetState", "WidgetDensity",
        "AccentToken", "VariantToken", "SurfaceToken",
    ],
    # Application & Windows
    "bootstack._runtime.app": ["App", "AppSettings", "Window", "get_app_settings", "get_current_app"],
    "bootstack._runtime.toplevel": ["Toplevel"],
    "bootstack._runtime.menu": ["MenuManager", "create_menu", "create_menu_items"],
    "bootstack._runtime.shortcuts": ["Shortcuts", "Shortcut", "get_shortcuts"],
    "bootstack.widgets.composites.appshell": ["AppShell"],
    # Style & Theming
    "bootstack.style": [
        "BootstrapIcon", "Font", "Style", "Typography",
        "get_style", "get_style_builder", "get_theme", "get_theme_provider",
        "set_theme", "get_theme_color", "toggle_theme", "get_themes", "register_user_theme",
    ],
    # Primitives
    "bootstack.widgets.primitives.badge": ["Badge"],
    "bootstack.widgets.primitives.button": ["Button"],
    "bootstack.widgets.primitives.card": ["Card"],
    "bootstack.widgets.primitives.checkbutton": ["CheckButton"],
    "bootstack.widgets.primitives.checktoggle": ["CheckToggle"],
    "bootstack.widgets.primitives.combobox": ["Combobox"],
    "bootstack.widgets.primitives.entry": ["Entry"],
    "bootstack.widgets.primitives.frame": ["Frame"],
    "bootstack.widgets.primitives.gridframe": ["GridFrame"],
    "bootstack.widgets.primitives.label": ["Label"],
    "bootstack.widgets.primitives.labelframe": ["LabelFrame"],
    "bootstack.widgets.primitives.menubutton": ["MenuButton"],
    "bootstack.widgets.primitives.notebook": ["Notebook"],
    "bootstack.widgets.primitives.optionmenu": ["OptionMenu"],
    "bootstack.widgets.primitives.packframe": ["PackFrame"],
    "bootstack.widgets.primitives.panedwindow": ["PanedWindow"],
    "bootstack.widgets.primitives.progressbar": ["Progressbar"],
    "bootstack.widgets.primitives.radiobutton": ["RadioButton"],
    "bootstack.widgets.primitives.radiotoggle": ["RadioToggle"],
    "bootstack.widgets.primitives.scale": ["Scale"],
    "bootstack.widgets.primitives.scrollbar": ["Scrollbar"],
    "bootstack.widgets.primitives.separator": ["Separator"],
    "bootstack.widgets.primitives.sizegrip": ["SizeGrip"],
    "bootstack.widgets.primitives.spinbox": ["Spinbox"],
    "bootstack.widgets.primitives.switch": ["Switch"],
    "bootstack.widgets.primitives.treeview": ["TreeView"],
    # Composites
    "bootstack.widgets.composites.accordion": ["Accordion"],
    "bootstack.widgets.composites.buttongroup": ["ButtonGroup"],
    "bootstack.widgets.composites.calendar": ["Calendar"],
    "bootstack.widgets.composites.contextmenu": ["ContextMenu", "ContextMenuItem"],
    "bootstack.widgets.composites.dateentry": ["DateEntry"],
    "bootstack.widgets.composites.dropdownbutton": ["DropdownButton"],
    "bootstack.widgets.composites.expander": ["Expander"],
    "bootstack.widgets.composites.field": ["Field", "FieldOptions"],
    "bootstack.widgets.composites.floodgauge": ["FloodGauge"],
    "bootstack.widgets.composites.form": ["Form"],
    "bootstack.widgets.composites.labeledscale": ["LabeledScale"],
    "bootstack.widgets.composites.compositeframe": ["CompositeFrame", "CompositeFrameKwargs"],
    "bootstack.widgets.composites.list": ["ListItem", "ListView"],
    "bootstack.widgets.composites.list.listitem": ["ListItemKwargs"],
    "bootstack.widgets.composites.menubar": ["MenuBar"],
    "bootstack.widgets.composites.meter": ["Meter"],
    "bootstack.widgets.composites.numericentry": ["NumericEntry"],
    "bootstack.widgets.composites.pagestack": ["PageStack"],
    "bootstack.widgets.composites.passwordentry": ["PasswordEntry"],
    "bootstack.widgets.composites.pathentry": ["PathEntry"],
    "bootstack.widgets.composites.radiogroup": ["RadioGroup"],
    "bootstack.widgets.composites.textarea": [
        "TextArea", "TextAreaInputEventData", "TextAreaValidationEventData",
        "CodeEditor",
    ],
    "bootstack.widgets.composites.textarea.filter": ["EditFilter"],
    "bootstack.widgets.composites.scrollview": ["ScrollView"],
    "bootstack.widgets.composites.selectbox": ["SelectBox"],
    "bootstack.widgets.composites.sidenav": ["SideNav", "SideNavItem", "SideNavGroup", "SideNavHeader", "SideNavSeparator"],
    "bootstack.widgets.composites.spinnerentry": ["SpinnerEntry"],
    "bootstack.widgets.composites.tableview": ["TableView"],
    "bootstack.widgets.composites.tabs.tabs": ["Tabs"],
    "bootstack.widgets.composites.tabs.tabview": ["TabView"],
    "bootstack.widgets.composites.tabs.tabitem": ["TabItem"],
    "bootstack.widgets.composites.tabs.events": [
        "TabRef", "TabChangeEventData", "TabActivateEventData",
        "TabDeactivateEventData", "ChangeReason", "ChangeMethod",
    ],
    "bootstack.widgets.composites.textentry": ["TextEntry"],
    "bootstack.widgets.composites.timeentry": ["TimeEntry"],
    "bootstack.widgets.composites.toast": ["Toast"],
    "bootstack.widgets.composites.togglegroup": ["ToggleGroup"],
    "bootstack.widgets.composites.toolbar": ["Toolbar"],
    "bootstack.widgets.composites.tooltip": ["ToolTip"],
    # Widget constants
    "bootstack.widgets": ["TK_WIDGETS", "TTK_WIDGETS"],
    # Dialogs
    "bootstack.dialogs": [
        "Dialog", "DialogButton", "FilterDialog", "FormDialog",
        "MessageDialog", "MessageBox", "QueryDialog", "QueryBox",
        "DateDialog", "FontDialog",
        "ColorChooser", "ColorChooserDialog", "ColorDropperDialog",
    ],
    # Data Sources
    "bootstack.data": [
        "BaseDataSource", "MemoryDataSource", "SqliteDataSource",
        "FileDataSource", "FileSourceConfig",
        "DataSourceProtocol", "Record", "Primitive",
    ],
    # Internationalization
    "bootstack.i18n": ["MessageCatalog", "L", "LV", "IntlFormatter"],
    # Utilities
    "bootstack._core.images": ["Image"],
    "bootstack.signals": ["Signal", "TraceOperation"],
    "bootstack.validation": ["ValidationRule", "ValidationResult"],
    "bootstack._core.variables": ["SetVar"],
}

# Auto-generate lazy exports and categorized export lists
_LAZY_EXPORTS = {}
_TTK_EXPORTS = _TTK_PRIMITIVES.copy()
_BOOTSTACK_EXPORTS = []

for module, exports in _MODULE_EXPORTS.items():
    for name in exports:
        _LAZY_EXPORTS[name] = module
        if name not in _TTK_EXPORTS:
            _BOOTSTACK_EXPORTS.append(name)

__all__ = [*_TK_EXPORTS, *_TTK_EXPORTS, *_BOOTSTACK_EXPORTS]

def __getattr__(name):
    """Lazily import top-level attributes to avoid circular imports and speed import."""
    if name in _LAZY_EXPORTS:
        module = _importlib.import_module(_LAZY_EXPORTS[name])
        value = getattr(module, name)
        globals()[name] = value
        return value

    raise AttributeError(f"module 'bootstack' has no attribute '{name}'")


def __dir__():
    return sorted(set(__all__ + list(globals().keys())))


# Patch Tk widgets for autostyle
from bootstack._runtime.tk_patch import install_tk_autostyle

# Install enhanced events on import
from bootstack._runtime.events import install_enhanced_events

# Install visual focus
from bootstack._runtime.visual_focus import install_visual_focus

install_tk_autostyle()
install_enhanced_events()
install_visual_focus()
