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
from bootstack.widgets.public import (
    # Infrastructure
    BootstackV2Error, UnknownEventError, ParentResolutionError,
    Event, Subscription, PublicWidgetBase, PublicContainer,
    # Dialogs
    alert, confirm, ask_string, ask_integer, ask_float, ask_date, ask_item,
    FormDialog, Dialog, DialogButton,
    # Application & layout
    App, AppShell, Window, HStack, VStack, Grid,
    # Widgets
    Accordion, Badge, Button, ButtonGroup, Card, Checkbox, CodeEditor,
    ContextMenu, ContextMenuItem, DateField, EditFilter, Expander, Gauge, GroupBox,
    Label, ListView, MenuBar, MenuButton, NumberField, PageStack,
    PathField, PasswordField, ProgressBar, Radio, RadioGroup,
    RadioToggleButton, RangeSlider, Scrollbar, ScrollView, Select,
    Separator, SizeGrip, SplitView, Slider, Spinbox, SpinnerField,
    Switch, Table, TableSelectionEventData, TableRowEventData, TableRowsEventData,
    TabChangeEventData, TabRef, Tabs, TextArea, TimeField, Tree,
    TextField, Toast, toast, ToggleButton, ToggleGroup, Toolbar, Tooltip,
)

# ── Unmigrated widgets (no public equivalent yet) ─────────────────────────────
from bootstack.widgets.composites.form import Form
from bootstack.widgets.composites.sidenav import (
    SideNav, SideNavItem, SideNavGroup, SideNavHeader, SideNavSeparator,
)
from bootstack.widgets.composites.calendar import Calendar