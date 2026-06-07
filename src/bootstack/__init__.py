"""bootstack — a Python desktop UI framework.

Build modern desktop apps with a clean, Pythonic API. No Tkinter knowledge required.

Example:
    ```python
    import bootstack as bs

    with bs.App(title="Hello") as app:
        bs.Label("Hello, world!")
    app.run()
    ```
"""
from importlib.metadata import version as _pkg_version

__version__ = _pkg_version("bootstack")

# ── Runtime patches — must run before widgets are created ─────────────────────
from bootstack._runtime.tk_patch import install_tk_autostyle as _install_autostyle
from bootstack._runtime.events import install_enhanced_events as _install_events
from bootstack._runtime.visual_focus import install_visual_focus as _install_focus

_install_autostyle()
_install_events()
_install_focus()

# ── Style & theming ───────────────────────────────────────────────────────────
from bootstack.style import (
    Theme,
    get_style, get_theme,
    set_theme, toggle_theme, get_theme_color, get_themes,
    get_font_families, set_font_family, update_font_token,
)

# ── Signals ───────────────────────────────────────────────────────────────────
from bootstack.signals import Signal, TraceOperation

# ── Data sources ──────────────────────────────────────────────────────────────
from bootstack.data import (
    BaseDataSource, MemoryDataSource, SqliteDataSource,
    FileDataSource, FileSourceConfig, DataSourceProtocol, Record, Primitive,
    col, any_of, all_of,
)

# ── Internationalization ──────────────────────────────────────────────────────
from bootstack.i18n import MessageCatalog, L, LV, IntlFormatter

# ── Validation ────────────────────────────────────────────────────────────────
from bootstack.validation import ValidationRule, ValidationResult

# ── Utilities ─────────────────────────────────────────────────────────────────
from bootstack._core.images import Image
from bootstack._runtime.app import AppSettings, get_app_settings, get_current_app
from bootstack.shortcuts import Shortcuts, Shortcut, get_shortcuts

# ── Widget type aliases ───────────────────────────────────────────────────────
from bootstack.widgets.types import (
    BaseWidgetKwargs, StyledKwargs,
    Anchor, BorderMode, CompoundMode, Direction,
    Fill, Justify, Orient, Relief, Side, Sticky,
    WidgetState, WidgetDensity,
    AccentToken, VariantToken, SurfaceToken,
)

# ── Public widget layer ───────────────────────────────────────────────────────
from bootstack.errors import BootstackError, UnknownEventError, ParentResolutionError, DuplicateIdError, SerializationError
# The typed event payloads (ChangeEvent, SliderEvent, …) live in the
# `bootstack.events` catalog — import them from there, not the top level.
from bootstack.events import Event, Subscription
from bootstack.scheduling import Schedule, Job
from bootstack.streams import Stream, Handle
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.container import PublicContainer
from bootstack.widgets.dialogs import (
    alert, confirm, ask_string, ask_integer, ask_float,
    ask_date, ask_date_range, ask_item,
    ask_color, ask_font, ask_filter,
    FormDialog, Dialog, DialogButton,
    ColorChooserDialog, ColorChoice,
    FontDialog, FontChoice,
    FilterDialog,
)
from bootstack.widgets.app import App
from bootstack.widgets.appshell import AppShell
from bootstack.widgets.window import Window
from bootstack.widgets.stacks import HStack, VStack
from bootstack.widgets.grid import Grid
from bootstack.widgets.boolean_controls import Checkbox, Switch, ToggleButton
from bootstack.widgets.button import Button
from bootstack.widgets.card import Card
from bootstack.widgets.buttongroup import ButtonGroup
from bootstack.widgets.codeeditor import CodeEditor
from bootstack.widgets.contextmenu import ContextMenu, ContextMenuItem
from bootstack.widgets.datefield import DateField
from bootstack.widgets._impl.composites.textarea.filter import EditFilter
from bootstack.widgets.expander import Accordion, AccordionSection
from bootstack.widgets.gauge import Gauge
from bootstack.widgets.groupbox import GroupBox
from bootstack.widgets.label import Badge, Label
from bootstack.widgets.listview import ListView
from bootstack.widgets.menubar import MenuBar
from bootstack.widgets.menubutton import MenuButton
from bootstack.widgets.numberfield import NumberField
from bootstack.widgets.pagestack import PageStack, StackPage
from bootstack.widgets.pathfield import PathField
from bootstack.widgets.passwordfield import PasswordField
from bootstack.widgets.progressbar import ProgressBar
from bootstack.widgets.radio_variants import Radio, RadioToggleButton
from bootstack.widgets.radiogroup import RadioGroup
from bootstack.widgets.scrollview import ScrollView
from bootstack.widgets.select import Select
from bootstack.widgets.selectbutton import SelectButton
from bootstack.widgets.separator import Separator
from bootstack.widgets.splitview import SplitView, SplitPane
from bootstack.widgets.slider import RangeSlider, Slider
from bootstack.widgets.spinnerfield import SpinnerField
from bootstack.widgets.datatable import DataTable
from bootstack.widgets.tabs import TabPage, Tabs
from bootstack.widgets.textarea import TextArea
from bootstack.widgets.timefield import TimeField
from bootstack.widgets.tree import Tree, TreeNode
from bootstack.widgets.textfield import TextField
from bootstack.widgets.toast import Toast, toast
from bootstack.widgets.togglegroup import ToggleGroup
from bootstack.widgets.toolbar import Toolbar
from bootstack.widgets.tooltip import Tooltip

from bootstack.widgets.calendar import Calendar
from bootstack.widgets.form import Form
from bootstack.widgets.form import FormItem, FieldItem, GroupItem, TabsItem, TabItem, EditorType

from bootstack.widgets.sidenav import (
    SideNav, SideNavItem, SideNavGroup, SideNavHeader, SideNavSeparator,
)


# ── Public API surface ────────────────────────────────────────────────────────
# The curated set of names that make up the public `bootstack` namespace.
__all__ = [
    "__version__",
    # Style & theming
    "Theme",
    "get_style", "get_theme", "set_theme", "toggle_theme",
    "get_theme_color", "get_themes",
    "get_font_families", "set_font_family", "update_font_token",
    # Signals
    "Signal", "TraceOperation",
    # Data sources
    "BaseDataSource", "MemoryDataSource", "SqliteDataSource", "FileDataSource",
    "FileSourceConfig", "DataSourceProtocol", "Record", "Primitive",
    "col", "any_of", "all_of",
    # Internationalization
    "MessageCatalog", "L", "LV", "IntlFormatter",
    # Validation
    "ValidationRule", "ValidationResult",
    # Events, streams, scheduling, errors
    "Event", "Subscription", "Stream", "Handle", "Schedule", "Job",
    "BootstackError", "UnknownEventError", "ParentResolutionError", "DuplicateIdError",
    "SerializationError",
    # App, shortcuts, images
    "AppSettings", "get_app_settings", "get_current_app",
    "Shortcuts", "Shortcut", "get_shortcuts", "Image",
    # Type aliases
    "BaseWidgetKwargs", "StyledKwargs", "Anchor", "BorderMode", "CompoundMode",
    "Direction", "Fill", "Justify", "Orient", "Relief", "Side", "Sticky",
    "WidgetState", "WidgetDensity", "AccentToken", "VariantToken", "SurfaceToken",
    # Extension base classes
    "PublicWidgetBase", "PublicContainer",
    # Dialogs
    "alert", "confirm", "ask_string", "ask_integer", "ask_float", "ask_date",
    "ask_date_range", "ask_item", "ask_color", "ask_font", "ask_filter",
    "FormDialog", "Dialog", "DialogButton", "ColorChooserDialog", "ColorChoice",
    "FontDialog", "FontChoice", "FilterDialog",
    # Application & windows
    "App", "AppShell", "Window",
    # Layout
    "HStack", "VStack", "Grid", "Card", "GroupBox", "Separator", "ScrollView",
    "SplitView", "SplitPane", "Accordion", "AccordionSection",
    # Actions
    "Button", "ButtonGroup", "MenuButton", "MenuBar", "Toolbar",
    "ContextMenu", "ContextMenuItem",
    # Inputs
    "TextField", "PasswordField", "NumberField", "PathField", "SpinnerField",
    "TextArea", "CodeEditor", "DateField", "TimeField", "Slider", "RangeSlider",
    "EditFilter",
    # Selection
    "Checkbox", "Switch", "ToggleButton", "ToggleGroup", "Radio",
    "RadioToggleButton", "RadioGroup", "Select", "SelectButton", "Calendar",
    # Data display
    "Label", "Badge", "ProgressBar", "Gauge", "ListView", "DataTable", "Tree", "TreeNode",
    # Navigation
    "PageStack", "StackPage", "Tabs", "TabPage",
    "SideNav", "SideNavItem", "SideNavGroup", "SideNavHeader", "SideNavSeparator",
    # Overlays
    "Tooltip", "Toast", "toast",
    # Forms
    "Form", "FormItem", "FieldItem", "GroupItem", "TabsItem", "TabItem",
    "EditorType",
]