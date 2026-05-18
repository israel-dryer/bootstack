"""Widget package for bootstack."""
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Static imports for type checkers and IDE support.
    # These are never executed at runtime — avoids the circular import that
    # eager aggregation would cause (style.style → widgets.types → widgets.__init__
    # → widget cascade → style.style).
    from bootstack.widgets.primitives.badge import Badge
    from bootstack.widgets.primitives.button import Button
    from bootstack.widgets.primitives.card import Card
    from bootstack.widgets.primitives.checkbutton import CheckButton
    from bootstack.widgets.primitives.checktoggle import CheckToggle
    from bootstack.widgets.primitives.combobox import Combobox
    from bootstack.widgets.primitives.entry import Entry
    from bootstack.widgets.primitives.frame import Frame
    from bootstack.widgets.primitives.gridframe import GridFrame
    from bootstack.widgets.primitives.label import Label
    from bootstack.widgets.primitives.labelframe import LabelFrame
    from bootstack.widgets.primitives.menubutton import MenuButton
    from bootstack.widgets.primitives.notebook import Notebook
    from bootstack.widgets.primitives.optionmenu import OptionMenu
    from bootstack.widgets.primitives.packframe import PackFrame
    from bootstack.widgets.primitives.panedwindow import PanedWindow
    from bootstack.widgets.primitives.progressbar import Progressbar
    from bootstack.widgets.primitives.radiobutton import RadioButton
    from bootstack.widgets.primitives.radiotoggle import RadioToggle
    from bootstack.widgets.primitives.scale import Scale
    from bootstack.widgets.primitives.scrollbar import Scrollbar
    from bootstack.widgets.primitives.separator import Separator
    from bootstack.widgets.primitives.sizegrip import SizeGrip
    from bootstack.widgets.primitives.spinbox import Spinbox
    from bootstack.widgets.primitives.switch import Switch
    from bootstack.widgets.primitives.treeview import TreeView
    from bootstack.widgets.composites.accordion import Accordion
    from bootstack.widgets.composites.appshell import AppShell
    from bootstack.widgets.composites.buttongroup import ButtonGroup
    from bootstack.widgets.composites.calendar import Calendar
    from bootstack.widgets.composites.compositeframe import CompositeFrame, CompositeFrameKwargs
    from bootstack.widgets.composites.contextmenu import ContextMenu, ContextMenuItem
    from bootstack.widgets.composites.dateentry import DateEntry
    from bootstack.widgets.composites.dropdownbutton import DropdownButton
    from bootstack.widgets.composites.expander import Expander
    from bootstack.widgets.composites.field import Field, FieldOptions
    from bootstack.widgets.composites.floodgauge import FloodGauge
    from bootstack.widgets.composites.form import Form
    from bootstack.widgets.composites.labeledscale import LabeledScale
    from bootstack.widgets.composites.list import ListItem, ListView
    from bootstack.widgets.composites.list.listitem import ListItemKwargs
    from bootstack.widgets.composites.menubar import MenuBar
    from bootstack.widgets.composites.meter import Meter
    from bootstack.widgets.composites.numericentry import NumericEntry
    from bootstack.widgets.composites.pagestack import PageStack
    from bootstack.widgets.composites.passwordentry import PasswordEntry
    from bootstack.widgets.composites.pathentry import PathEntry
    from bootstack.widgets.composites.radiogroup import RadioGroup
    from bootstack.widgets.composites.textarea import TextArea, CodeEditor
    from bootstack.widgets.composites.textarea.filter import EditFilter
    from bootstack.widgets.composites.scrollview import ScrollView
    from bootstack.widgets.composites.selectbox import SelectBox
    from bootstack.widgets.composites.sidenav import (
        SideNav, SideNavItem, SideNavGroup, SideNavHeader, SideNavSeparator,
    )
    from bootstack.widgets.composites.spinnerentry import SpinnerEntry
    from bootstack.widgets.composites.tableview import TableView
    from bootstack.widgets.composites.tabs.tabs import Tabs
    from bootstack.widgets.composites.tabs.tabview import TabView
    from bootstack.widgets.composites.tabs.tabitem import TabItem
    from bootstack.widgets.composites.tabs.events import (
        TabRef, TabChangeEventData, TabActivateEventData, TabDeactivateEventData,
        ChangeReason, ChangeMethod,
    )
    from bootstack.widgets.composites.textentry import TextEntry
    from bootstack.widgets.composites.timeentry import TimeEntry
    from bootstack.widgets.composites.toast import Toast
    from bootstack.widgets.composites.togglegroup import ToggleGroup
    from bootstack.widgets.composites.toolbar import Toolbar
    from bootstack.widgets.composites.tooltip import ToolTip

TTK_WIDGETS = (
    ttk.Button,
    ttk.Checkbutton,
    ttk.Combobox,
    ttk.Entry,
    ttk.Frame,
    ttk.Labelframe,
    ttk.Label,
    ttk.Menubutton,
    ttk.Notebook,
    ttk.Panedwindow,
    ttk.Progressbar,
    ttk.Radiobutton,
    ttk.Scale,
    ttk.Scrollbar,
    ttk.Separator,
    ttk.Sizegrip,
    ttk.Spinbox,
    ttk.Treeview,
    ttk.OptionMenu,
)

TK_WIDGETS = (
    tk.Tk,
    tk.Toplevel,
    tk.Button,
    tk.Label,
    tk.Text,
    tk.Frame,
    tk.Checkbutton,
    tk.Radiobutton,
    tk.Entry,
    tk.Scale,
    tk.Listbox,
    tk.Menu,
    tk.Menubutton,
    tk.LabelFrame,
    tk.Canvas,
    tk.OptionMenu,
    tk.Spinbox,
)

__all__ = [
    'TTK_WIDGETS', 'TK_WIDGETS',
    # Primitives
    'Badge', 'Button', 'Card', 'CheckButton', 'CheckToggle', 'Combobox',
    'Entry', 'Frame', 'GridFrame', 'Label', 'LabelFrame', 'MenuButton',
    'Notebook', 'OptionMenu', 'PackFrame', 'PanedWindow', 'Progressbar',
    'RadioButton', 'RadioToggle', 'Scale', 'Scrollbar', 'Separator',
    'SizeGrip', 'Spinbox', 'Switch', 'TreeView',
    # Composites
    'Accordion', 'AppShell', 'ButtonGroup', 'Calendar', 'CompositeFrame',
    'CompositeFrameKwargs', 'ContextMenu', 'ContextMenuItem', 'DateEntry',
    'DropdownButton', 'Expander', 'Field', 'FieldOptions', 'FloodGauge',
    'Form', 'LabeledScale', 'ListItem', 'ListItemKwargs', 'ListView',
    'MenuBar', 'Meter', 'NumericEntry', 'PageStack', 'PasswordEntry',
    'PathEntry', 'RadioGroup', 'TextArea', 'CodeEditor', 'EditFilter', 'ScrollView', 'SelectBox',
    'SideNav', 'SideNavItem', 'SideNavGroup', 'SideNavHeader', 'SideNavSeparator',
    'SpinnerEntry', 'TableView', 'TabItem', 'Tabs', 'TabView',
    'TabRef', 'TabChangeEventData', 'TabActivateEventData', 'TabDeactivateEventData',
    'ChangeReason', 'ChangeMethod',
    'TextEntry', 'TimeEntry', 'Toast',
    'ToggleGroup', 'Toolbar', 'ToolTip',
]
