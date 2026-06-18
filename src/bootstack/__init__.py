"""bootstack — a Python desktop UI framework.

Build modern desktop apps with a clean, Pythonic API. No Tkinter knowledge required.

Example:
    ```python
    import bootstack as bs

    with bs.App(title="Hello") as app:
        bs.Label("Hello, world!")
    app.run()
    ```

The top-level `bootstack` namespace holds what you *compose a UI* with: every
widget, `App`/`AppShell`/`Window`, `Signal`, the dialog verbs
(`alert`/`confirm`/`ask_*`/`toast`), and `set_theme`/`toggle_theme`.
Framework primitives you reference *by type to configure behavior* live in
submodules — for example::

    from bootstack.data import SqliteDataSource, col
    from bootstack.i18n import L, LV
    from bootstack.validation import ValidationRule
    from bootstack.style import Theme, get_theme_color
    from bootstack.events import Event, Subscription
    from bootstack.images import Image, get_icon, AppIcon
    from bootstack.types import AccentToken

See the "API overview" in the documentation for the full map.
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

# ── Reactive state ────────────────────────────────────────────────────────────
from bootstack.signals import Signal

# ── Theme switching (full theming API lives in `bootstack.style`) ─────────────
from bootstack.style import set_theme, toggle_theme

# ── Dialog verbs (dialog classes live in `bootstack.dialogs`) ─────────────────
from bootstack.dialogs import (
    alert, confirm, ask_string, ask_integer, ask_float,
    ask_date, ask_date_range, ask_item,
    ask_color, ask_font, ask_filter,
    ask_save_file, ask_open_file, ask_open_files, ask_directory,
)

# ── Application & windows ─────────────────────────────────────────────────────
from bootstack.widgets.app import App
from bootstack.widgets.appshell import AppShell
from bootstack.widgets.window import Window

# ── Public widget layer ───────────────────────────────────────────────────────
from bootstack.widgets.stacks import Row, Column, Spacer
from bootstack.widgets.grid import Grid
from bootstack.widgets.boolean_controls import Checkbox, Switch, ToggleButton
from bootstack.widgets.theme_toggle import ThemeToggle
from bootstack.widgets.button import Button
from bootstack.widgets.card import Card
from bootstack.widgets.buttongroup import ButtonGroup
from bootstack.widgets.codeeditor import CodeEditor
from bootstack.widgets.contextmenu import ContextMenu, ContextMenuItem
from bootstack.widgets.datefield import DateField
from bootstack.widgets.expander import Accordion, AccordionSection
from bootstack.widgets.gauge import Gauge
from bootstack.widgets.groupbox import GroupBox
from bootstack.widgets.label import Badge, Label
from bootstack.widgets.listview import ListView
from bootstack.widgets.menubutton import MenuButton
from bootstack.widgets.numberfield import NumberField
from bootstack.widgets.pagestack import PageStack, StackPage
from bootstack.widgets.pathfield import PathField
from bootstack.widgets.avatar import Avatar
from bootstack.widgets.carousel import Carousel
from bootstack.widgets.gallery import Gallery
from bootstack.widgets.passwordfield import PasswordField
from bootstack.widgets.picture import Picture
from bootstack.widgets.progressbar import ProgressBar
from bootstack.widgets.radio_variants import Radio, RadioToggleButton
from bootstack.widgets.radiogroup import RadioGroup
from bootstack.widgets.scrollview import ScrollView
from bootstack.widgets.select import Select
from bootstack.widgets.selectbutton import SelectButton
from bootstack.widgets.divider import Divider
from bootstack.widgets.splitview import SplitView, SplitPane
from bootstack.widgets.slider import RangeSlider, Slider
from bootstack.widgets.spinnerfield import SpinnerField
from bootstack.widgets.datatable import DataTable
from bootstack.widgets.tabs import TabPage, Tabs
from bootstack.widgets.textarea import TextArea
from bootstack.widgets.timefield import TimeField
from bootstack.widgets.tree import Tree, TreeNode
from bootstack.widgets.textfield import TextField
from bootstack.widgets.toast import toast, Notification, Snackbar, snackbar
from bootstack.widgets.togglegroup import ToggleGroup
from bootstack.widgets.toolbar import Toolbar
from bootstack.widgets.statusbar import StatusBar
from bootstack.widgets.tooltip import Tooltip

from bootstack.widgets.calendar import Calendar
from bootstack.widgets.form import Form
from bootstack.widgets.form import FormItem, FieldItem, GroupItem, TabsItem, TabItem


# ── Public API surface ────────────────────────────────────────────────────────
# The curated top-level namespace: things you compose a UI with. Framework
# primitives (data, i18n, validation, events, streams, scheduling, shortcuts,
# style, errors, store, types) live in their own submodules — see the docs'
# "API overview". This list is kept in sync with tests/test_public_surface.py.
__all__ = [
    "__version__",
    # Reactive state
    "Signal",
    # Theme switching
    "set_theme", "toggle_theme",
    # Dialog verbs
    "alert", "confirm", "ask_string", "ask_integer", "ask_float", "ask_date",
    "ask_date_range", "ask_item", "ask_color", "ask_font", "ask_filter",
    "ask_save_file", "ask_open_file", "ask_open_files", "ask_directory",
    # Application & windows
    "App", "AppShell", "Window",
    # Layout
    "Row", "Column", "Spacer", "Grid", "Card", "GroupBox", "Divider", "ScrollView",
    "SplitView", "SplitPane", "Accordion", "AccordionSection",
    # Actions
    "Button", "ButtonGroup", "ThemeToggle", "MenuButton", "Toolbar", "StatusBar",
    "ContextMenu", "ContextMenuItem",
    # Inputs
    "TextField", "PasswordField", "NumberField", "PathField", "SpinnerField",
    "TextArea", "CodeEditor", "DateField", "TimeField", "Slider", "RangeSlider",
    # Selection
    "Checkbox", "Switch", "ToggleButton", "ToggleGroup", "Radio",
    "RadioToggleButton", "RadioGroup", "Select", "SelectButton", "Calendar",
    # Data display
    "Label", "Badge", "ProgressBar", "Gauge", "ListView", "DataTable", "Tree", "TreeNode",
    # Media
    "Picture", "Gallery", "Carousel", "Avatar",
    # Navigation
    "PageStack", "StackPage", "Tabs", "TabPage",
    # Overlays
    "Tooltip", "toast", "Notification", "Snackbar", "snackbar",
    # Forms
    "Form", "FormItem", "FieldItem", "GroupItem", "TabsItem", "TabItem",
]
