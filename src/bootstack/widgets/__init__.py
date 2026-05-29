"""Widget package for bootstack."""
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bootstack.widgets.dialogs import (
        alert, confirm,
        ask_string, ask_integer, ask_float, ask_date, ask_item,
        FormDialog, Dialog, DialogButton,
    )
    from bootstack.widgets._core.events import Event
    from bootstack.widgets._core.exceptions import BootstackV2Error, UnknownEventError, ParentResolutionError
    from bootstack.widgets._core.subscription import Subscription
    from bootstack.widgets._core.container import PublicContainer
    from bootstack.widgets._core.base import PublicWidgetBase
    from bootstack.widgets.stacks import HStack, VStack
    from bootstack.widgets.grid import Grid
    from bootstack.widgets.app import App
    from bootstack.widgets.appshell import AppShell
    from bootstack.widgets.window import Window
    from bootstack.widgets.boolean_controls import Checkbox, Switch, ToggleButton
    from bootstack.widgets.button import Button
    from bootstack.widgets.buttongroup import ButtonGroup
    from bootstack.widgets.contextmenu import ContextMenu, ContextMenuItem
    from bootstack.widgets.codeeditor import CodeEditor
    from bootstack.widgets._impl.composites.textarea.filter import EditFilter
    from bootstack.widgets.datefield import DateField
    from bootstack.widgets.expander import Accordion, Expander
    from bootstack.widgets.gauge import Gauge
    from bootstack.widgets.groupbox import GroupBox
    from bootstack.widgets.label import Badge, Label
    from bootstack.widgets.listview import ListView
    from bootstack.widgets.menubutton import MenuButton
    from bootstack.widgets.numberfield import NumberField
    from bootstack.widgets.pagestack import PageStack
    from bootstack.widgets.pathfield import PathField
    from bootstack.widgets.passwordfield import PasswordField
    from bootstack.widgets.progressbar import ProgressBar
    from bootstack.widgets.radio_variants import Radio, RadioToggleButton
    from bootstack.widgets.radiogroup import RadioGroup
    from bootstack.widgets.menubar import MenuBar
    from bootstack.widgets.scrollbar import Scrollbar
    from bootstack.widgets.scrollview import ScrollView
    from bootstack.widgets.select import Select
    from bootstack.widgets.separator import Separator
    from bootstack.widgets.sizegrip import SizeGrip
    from bootstack.widgets.splitview import SplitView
    from bootstack.widgets.slider import RangeSlider, Slider
    from bootstack.widgets.spinbox import Spinbox
    from bootstack.widgets.spinnerfield import SpinnerField
    from bootstack.widgets.timefield import TimeField
    from bootstack.widgets.table import Table, TableSelectionEventData, TableRowEventData, TableRowsEventData
    from bootstack.widgets.tabs import TabChangeEventData, TabRef, Tabs
    from bootstack.widgets.textarea import TextArea
    from bootstack.widgets.tree import Tree
    from bootstack.widgets.textfield import TextField
    from bootstack.widgets.toast import Toast, toast
    from bootstack.widgets.togglegroup import ToggleGroup
    from bootstack.widgets.toolbar import Toolbar
    from bootstack.widgets.tooltip import Tooltip

TTK_WIDGETS = (
    ttk.Button,
    ttk.Checkbutton,
    ttk.Combobox,
    ttk.Entry,
    ttk.Frame,
    ttk.Labelframe,
    ttk.Label,
    ttk.Menubutton,
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