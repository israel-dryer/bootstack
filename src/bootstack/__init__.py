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
    from bootstack.api.menu import MenuManager, create_menu
    from bootstack.api.app import App, AppShell, App as Window, Toplevel, AppSettings, get_app_settings, get_current_app, Shortcuts, Shortcut, get_shortcuts
    from bootstack.api.style import (
        Font,
        Style,
        Typography,
        get_style,
        get_style_builder,
        get_theme,
        get_theme_provider,
        set_theme,
        toggle_theme,
        get_theme_color,
        get_themes,
        register_user_theme,
    )
    from bootstack.api.widgets import (
        Button,
        ButtonGroup,
        Card,
        CheckButton,
        Combobox,
        ContextMenu,
        ContextMenuItem,
        DateEntry,
        Calendar,
        DropdownButton,
        Entry,
        Field,
        FieldOptions,
        FloodGauge,
        Form,
        Frame,
        GridFrame,
        Label,
        LabelFrame,
        LabeledScale,
        ListItem,
        ListView,
        MenuBar,
        MenuButton,
        Meter,
        SideNav,
        SideNavItem,
        SideNavGroup,
        SideNavHeader,
        SideNavSeparator,
        Notebook,
        NumericEntry,
        OptionMenu,
        PackFrame,
        PageStack,
        PanedWindow,
        PasswordEntry,
        PathEntry,
        Progressbar,
        RadioButton,
        RadioGroup,
        Scale,
        Scrollbar,
        ScrolledText,
        ScrollView,
        SelectBox,
        Separator,
        SideNav,
        SpinnerEntry,
        SizeGrip,
        Spinbox,
        Switch,
        TableView,
        TextEntry,
        TimeEntry,
        Toast,
        Toolbar,
        ToggleGroup,
        ToolTip,
        TreeView,
        TK_WIDGETS,
        TTK_WIDGETS,
    )
    from bootstack.api.localization import MessageCatalog, L, LV, IntlFormatter
    from bootstack.api.utils import Image
    from ttkbootstrap_icons_bs import BootstrapIcon


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
    # Application & Windows (includes menu and shortcuts)
    "bootstack.api.app": [
        "App", "AppShell", "Toplevel", "Window", "AppSettings", "get_app_settings", "get_current_app",
        "MenuManager", "create_menu",
        "Shortcuts", "Shortcut", "get_shortcuts",
    ],
    # Style & Theming
    "bootstack.api.style": [
        "BootstrapIcon", "Font", "Style", "Typography",
        "get_style", "get_style_builder", "get_theme",
        "get_theme_provider", "set_theme", "get_theme_color",
        "toggle_theme", "get_themes",
        "register_user_theme",
    ],
    # Widgets
    "bootstack.api.widgets": [
        *_TTK_PRIMITIVES,
        "Badge",
        "ButtonGroup",
        "Card",
        "CheckToggle",
        "RadioToggle",
        "Calendar", "ContextMenu", "ContextMenuItem", "DateEntry",
        "Accordion", "DropdownButton", "Expander", "Field", "FieldOptions", "FloodGauge", "Form",
        "GridFrame", "LabeledScale", "ListItem", "ListView", "MenuBar", "Meter",
        "SideNav", "SideNavItem", "SideNavGroup",
        "SideNavHeader", "SideNavSeparator",
        "NumericEntry", "PackFrame", "PageStack",
        "PasswordEntry", "PathEntry", "RadioGroup", "ScrolledText", "ScrollView", "SpinnerEntry",
        "SelectBox", "TableView", "TextEntry", "TimeEntry", "Toast", "Toolbar", "ToggleGroup", "Switch",
        "ToolTip", "TK_WIDGETS", "TTK_WIDGETS",
    ],
    # Dialogs
    "bootstack.api.dialogs": [
        "Dialog", "DialogButton", "FilterDialog", "FormDialog",
        "MessageDialog", "MessageBox", "QueryDialog", "QueryBox",
        "DateDialog", "FontDialog",
        "ColorChooser", "ColorChooserDialog", "ColorDropperDialog",
    ],
    # Data Sources
    "bootstack.api.data": [
        "BaseDataSource", "MemoryDataSource", "SqliteDataSource",
        "FileDataSource", "FileSourceConfig",
        "DataSourceProtocol", "Record", "Primitive",
    ],
    # Internationalization
    "bootstack.api.i18n": [
        "MessageCatalog", "L", "LV", "IntlFormatter"
    ],
    # Utilities
    "bootstack.api.utils": [
        "Image",
        "Signal", "TraceOperation",
        "ValidationRule", "ValidationResult",
        "SetVar",
    ],
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
from bootstack.runtime.tk_patch import install_tk_autostyle

# Install enhanced events on import
from bootstack.runtime.events import install_enhanced_events

# Install visual focus
from bootstack.runtime.visual_focus import install_visual_focus

install_tk_autostyle()
install_enhanced_events()
install_visual_focus()
