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
    Font, Style, Typography,
    get_style, get_style_builder, get_theme, get_theme_provider,
    set_theme, toggle_theme, get_theme_color, get_themes, register_user_theme,
)

# ── Signals ───────────────────────────────────────────────────────────────────
from bootstack.signals import Signal, TraceOperation

# ── Data sources ──────────────────────────────────────────────────────────────
from bootstack.data import (
    BaseDataSource, MemoryDataSource, SqliteDataSource,
    FileDataSource, FileSourceConfig, DataSourceProtocol, Record, Primitive,
)

# ── Internationalization ──────────────────────────────────────────────────────
from bootstack.i18n import MessageCatalog, L, LV, IntlFormatter

# ── Validation ────────────────────────────────────────────────────────────────
from bootstack.validation import ValidationRule, ValidationResult

# ── Utilities ─────────────────────────────────────────────────────────────────
from bootstack._core.images import Image
from bootstack._core.variables import SetVar
from bootstack._runtime.app import AppSettings, get_app_settings, get_current_app
from bootstack._runtime.shortcuts import Shortcuts, Shortcut, get_shortcuts
from bootstack._runtime.menu import MenuManager, create_menu, create_menu_items

# ── Widget type aliases ───────────────────────────────────────────────────────
from bootstack.widgets.types import (
    BaseWidgetKwargs, StyledKwargs,
    Anchor, BorderMode, CompoundMode, Direction,
    Fill, Justify, Orient, Relief, Side, Sticky,
    WidgetState, WidgetDensity,
    AccentToken, VariantToken, SurfaceToken,
)

# ── Public widget layer ───────────────────────────────────────────────────────
from bootstack.widgets._core.events import Event
from bootstack.widgets._core.exceptions import BootstackV2Error, UnknownEventError, ParentResolutionError
from bootstack.widgets._core.subscription import Subscription
from bootstack.widgets._core.schedule import Schedule, Job
from bootstack.widgets._core.stream import Stream, Handle
from bootstack.widgets._core.base import PublicWidgetBase
from bootstack.widgets._core.container import PublicContainer
from bootstack.widgets.dialogs import (
    alert, confirm, ask_string, ask_integer, ask_float,
    ask_date, ask_date_range, ask_item,
    ask_color, ask_font, ask_filter,
    FormDialog, Dialog, DialogButton,
    ColorChooserDialog, ColorChoice,
    FontDialog,
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
from bootstack.widgets.scrollbar import Scrollbar
from bootstack.widgets.scrollview import ScrollView
from bootstack.widgets.select import Select
from bootstack.widgets.selectbutton import SelectButton
from bootstack.widgets.separator import Separator
from bootstack.widgets.sizegrip import SizeGrip
from bootstack.widgets.splitview import SplitView, SplitPane
from bootstack.widgets.slider import RangeSlider, Slider
from bootstack.widgets.spinbox import Spinbox
from bootstack.widgets.spinnerfield import SpinnerField
from bootstack.widgets.table import Table, TableSelectionEventData, TableRowEventData, TableRowsEventData
from bootstack.widgets.tabs import TabChangeEventData, TabPage, TabRef, Tabs
from bootstack.widgets.textarea import TextArea
from bootstack.widgets.timefield import TimeField
from bootstack.widgets.tree import Tree
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