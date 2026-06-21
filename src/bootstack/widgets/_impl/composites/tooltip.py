import tkinter as tk
from tkinter import Misc
from types import SimpleNamespace
from typing import Any, Literal

from bootstack.constants import *
from bootstack._runtime.toplevel import Toplevel
from bootstack._runtime.utility import scale_size
from bootstack._runtime.window_utilities import WindowPositioning, AnchorPoint
from bootstack.widgets._impl.primitives import Button, Frame, Label

ttk = SimpleNamespace(
    Button=Button,
    Frame=Frame,
    Label=Label,
    window=SimpleNamespace(Toplevel=Toplevel),
)


class ToolTip:
    # Position offset from mouse pointer
    _MOUSE_OFFSET_X = 25
    _MOUSE_OFFSET_Y = 10

    # Spacing between tooltip and widget when anchored
    _WIDGET_SPACING = 1

    # Fallback dimensions for tooltip sizing
    _FALLBACK_WIDTH = 200
    _FALLBACK_HEIGHT = 50

    def __init__(
            self,
            widget: Misc,
            text: str = "widget info",
            padding: int = 10,
            justify: Literal["left", "center", "right"] = "left",
            accent: str | None = None,
            wraplength: int | None = None,
            delay: int = 250,  # milliseconds
            image: Any = None,
            anchor_point: AnchorPoint | None = None,
            window_point: AnchorPoint | None = None,
            auto_flip: bool | Literal['vertical', 'horizontal'] = True,
            **kwargs: Any,
    ) -> None:
        """Initialize a ToolTip instance for the specified widget.

        Creates a tooltip that appears after a configurable delay when the mouse
        enters the widget and disappears when the mouse leaves or on button press.
        The tooltip can either follow the mouse pointer or be anchored to a specific
        position relative to the widget.

        The tooltip window is created with semi-transparency (alpha=0.95 by default)
        and uses the Bootstrap styling system for consistent theming. Text automatically
        wraps based on the specified wraplength, and optional images can be displayed
        alongside the text.

        Args:
            widget: The tkinter widget to attach this tooltip to. The tooltip will
                appear when hovering over this widget.
            text: The text content to display in the tooltip. Supports multi-line
                text that will wrap according to wraplength. Defaults to "widget info".
            padding: The internal padding in pixels between the tooltip text and the
                tooltip border. Defaults to 10.
            justify: Text alignment within the tooltip. Valid options are "left",
                "center", or "right". Defaults to "left".
            accent: Accent token for the tooltip frame (e.g., "danger", "info").
                If None, uses default elevated background styling.
                to the tooltip frame.
            wraplength: Maximum width in screen units before text wraps to a new line.
                If None, defaults to a scaled value of 300 based on the widget's display.
            delay: Time in milliseconds to wait before showing the tooltip after mouse
                enters the widget. Defaults to 250ms.
            image: Optional image to display in the tooltip below the text. Should be
                a PhotoImage or compatible tkinter image object.
            anchor_point: Point on the widget to anchor to (n, s, e, w, ne, nw, se, sw, center).
                If None, tooltip follows the mouse pointer.
            window_point: Point on the tooltip window to align with anchor_point
                (n, s, e, w, ne, nw, se, sw, center). If None, auto-defaults to the
                opposite of anchor_point for natural positioning.
            auto_flip: Smart positioning to keep tooltip on screen. Defaults to True.
                - False: No flipping
                - True: Flip both vertically and horizontally as needed
                - 'vertical': Only flip up/down
                - 'horizontal': Only flip left/right
            **kwargs: Additional keyword arguments passed to the Toplevel window
                constructor. Common options include alpha, topmost, etc. The arguments
                overrideredirect, master, and windowtype are set automatically.
        """
        # Configuration
        self._widget = widget
        self._text = text
        self._padding = padding
        self._justify = justify
        self._accent = accent
        self._wraplength = wraplength if wraplength is not None else scale_size(self._widget, 300)
        self._delay = delay
        self._image = image
        self._anchor_point = anchor_point
        self._window_point = window_point
        self._auto_flip = auto_flip

        self._toplevel = None
        self._label = None
        self._id = None

        # Set keyword arguments (create copy to avoid mutating caller's dict)
        self.toplevel_kwargs = kwargs.copy()
        self.toplevel_kwargs["overrideredirect"] = True
        self.toplevel_kwargs["master"] = self._widget
        self.toplevel_kwargs["windowtype"] = "tooltip"
        if "alpha" not in self.toplevel_kwargs:
            self.toplevel_kwargs["alpha"] = 0.95

        # Event binding. add="+" so we never replace a handler the target
        # already has; keep the bind ids so destroy() removes only our own.
        self._bind_ids = {
            "<Enter>": self._widget.bind("<Enter>", self._on_enter, add="+"),
            "<Leave>": self._widget.bind("<Leave>", self._on_leave, add="+"),
            "<Motion>": self._widget.bind("<Motion>", self._move_tip, add="+"),
            "<ButtonPress>": self._widget.bind("<ButtonPress>", self._on_button_press, add="+"),
        }
        # Self-release when the target is destroyed, so a pending timer or a
        # visible popup can't outlive it (and a later destroy() can't crash on a
        # dead widget). <Destroy> propagates up from descendants that carry the
        # target's bindtag, so the handler guards on the target itself.
        self._destroy_id = self._widget.bind("<Destroy>", self._on_target_destroy, add="+")

        # Tk events don't bubble, so hovering a child of a container target
        # would otherwise never reach these bindings. Extend them across the
        # subtree so the tip shows anywhere inside the container.
        from bootstack._runtime.utility import propagate_target_bindings
        propagate_target_bindings(self._widget)

    def destroy(self) -> None:
        """Cleanup tooltip resources and unbind all event handlers.

        This method should be called when the tooltip is no longer needed to prevent
        memory leaks. It cancels any pending tooltip display, hides any visible tooltip,
        and removes all event bindings from the widget.
        """
        self._unschedule()
        self._hide_tip()
        # The target may already be gone (e.g. destroyed before destroy() is
        # called); unbinding a dead widget path raises a TclError, so guard it.
        try:
            if self._widget.winfo_exists():
                for sequence, bind_id in self._bind_ids.items():
                    self._widget.unbind(sequence, bind_id)
                if self._destroy_id:
                    self._widget.unbind("<Destroy>", self._destroy_id)
        except tk.TclError:
            pass
        self._bind_ids = {}
        self._destroy_id = None

    @property
    def text(self) -> str:
        """The tooltip text. Assigning updates a visible popup live."""
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        if self._toplevel is not None and self._label is not None:
            try:
                self._label.configure(text=value)
            except tk.TclError:
                pass

    def _on_target_destroy(self, event: Any) -> None:
        """Release the timer and popup when the target widget is destroyed."""
        if event.widget is not self._widget:
            return  # a descendant was destroyed, not the target itself
        self._unschedule()
        self._hide_tip()

    def _on_enter(self, _) -> None:
        """Handle mouse enter event by scheduling tooltip display."""
        self._schedule()

    def _on_leave(self, _) -> None:
        """Handle mouse leave event by canceling and hiding tooltip.

        When the target is a container, crossing from the container onto one of
        its children fires a `<Leave>` on the container even though the pointer
        is still inside it. Keep the tip in that case so it doesn't flicker as
        the pointer moves over child widgets.
        """
        if self._pointer_within_target():
            return
        self._unschedule()
        self._hide_tip()

    def _on_button_press(self, _) -> None:
        """Hide the tooltip on any button press inside the target subtree."""
        self._unschedule()
        self._hide_tip()

    def _pointer_within_target(self) -> bool:
        """Return True if the pointer is over the target or one of its children."""
        try:
            x = self._widget.winfo_pointerx()
            y = self._widget.winfo_pointery()
            under = self._widget.winfo_containing(x, y)
        except tk.TclError:
            return False
        if under is None:
            return False
        target_path = str(self._widget)
        under_path = str(under)
        return under_path == target_path or under_path.startswith(target_path + ".")

    def _schedule(self) -> None:
        """Schedule the tooltip to appear after the configured delay."""
        self._unschedule()
        self._id = self._widget.after(self._delay, self._show_tip)

    def _unschedule(self) -> None:
        """Cancel any pending scheduled tooltip display."""
        _id = self._id
        self._id = None
        if _id:
            self._widget.after_cancel(_id)

    def _show_tip(self, *_: Any) -> None:
        """Create and display the tooltip window at the appropriate position."""
        if self._toplevel:
            return

        # Check if widget still exists before showing tooltip
        try:
            if not self._widget.winfo_exists():
                return
        except tk.TclError:
            return

        # Create the tooltip window (position will be set after content is built)
        self._toplevel = Toplevel(**self.toplevel_kwargs)
        # Use accent with tooltip variant
        accent = 'background[+1]' if self._accent is None else self._accent
        frame = ttk.Frame(
            self._toplevel,
            accent=accent,
            variant='tooltip',
            padding=self._padding
        )
        frame.pack(fill=BOTH, expand=YES)

        lbl = ttk.Label(
            master=frame,
            text=self._text,
            image=self._image,
            compound='bottom',
            justify=self._justify,
            font="caption",
            wraplength=self._wraplength,
        )
        lbl.pack(fill=BOTH, expand=YES)
        self._label = lbl

        # Wait until size is known, then position
        self._toplevel.update_idletasks()

        if self._anchor_point:
            # Use WindowPositioning for anchored tooltips (sets geometry directly)
            self._position_anchored()
        else:
            # Mouse-following tooltip
            x, y = self._get_mouse_position()
            self._toplevel.geometry(f"+{x}+{y}")

        # Ensure the tooltip is visible
        self._toplevel.deiconify()

    def _move_tip(self, *_: Any) -> None:
        """Update the tooltip position based on mouse or anchor position."""
        if self._toplevel:
            if self._anchor_point:
                # Anchored tooltips don't move
                pass
            else:
                # Update mouse-following tooltip
                x, y = self._get_mouse_position()
                self._toplevel.geometry(f"+{x}+{y}")

    def _hide_tip(self, *_: Any) -> None:
        """Hide and destroy the tooltip window."""
        if self._toplevel:
            self._toplevel.destroy()
            self._toplevel = None
            self._label = None

    def _get_mouse_position(self) -> tuple[int, int]:
        """Get tooltip position offset from the current mouse pointer.

        Uses WindowPositioning to ensure the tooltip stays on screen.

        Returns:
            Tuple of (x, y) screen coordinates for the tooltip.
        """
        x = self._widget.winfo_pointerx() + self._MOUSE_OFFSET_X
        y = self._widget.winfo_pointery() + self._MOUSE_OFFSET_Y

        # Ensure tooltip stays on screen (no titlebar since overrideredirect=True)
        if self._toplevel:
            x, y = WindowPositioning.ensure_on_screen(
                self._toplevel, x, y, padding=5, titlebar_height=0
            )

        return x, y

    def _position_anchored(self) -> None:
        """Position tooltip using WindowPositioning for intelligent anchor-based positioning.

        Uses anchor_point and window_point attributes and applies auto-flip
        to keep tooltip on screen.
        """
        if not self._toplevel or not self._anchor_point:
            return

        # Ensure the widget is fully laid out before calculating position
        self._widget.update_idletasks()

        # Default window_point based on anchor_point if not specified
        window_point = self._window_point
        if window_point is None:
            # Auto-determine opposite anchor point for natural positioning
            opposite = {
                'n': 's', 's': 'n', 'e': 'w', 'w': 'e',
                'ne': 'sw', 'nw': 'se', 'se': 'nw', 'sw': 'ne',
                'center': 'center'
            }
            window_point = opposite.get(self._anchor_point, 's')

        # Get widget dimensions using max of requested and actual size
        widget_x = self._widget.winfo_rootx()
        widget_y = self._widget.winfo_rooty()
        widget_w = max(self._widget.winfo_reqwidth(), self._widget.winfo_width())
        widget_h = max(self._widget.winfo_reqheight(), self._widget.winfo_height())

        # Calculate anchor coordinates based on anchor_point
        if self._anchor_point == 'nw':
            anchor_x, anchor_y = widget_x, widget_y
        elif self._anchor_point == 'n':
            anchor_x, anchor_y = widget_x + widget_w // 2, widget_y
        elif self._anchor_point == 'ne':
            anchor_x, anchor_y = widget_x + widget_w, widget_y
        elif self._anchor_point == 'w':
            anchor_x, anchor_y = widget_x, widget_y + widget_h // 2
        elif self._anchor_point == 'center':
            anchor_x, anchor_y = widget_x + widget_w // 2, widget_y + widget_h // 2
        elif self._anchor_point == 'e':
            anchor_x, anchor_y = widget_x + widget_w, widget_y + widget_h // 2
        elif self._anchor_point == 'sw':
            anchor_x, anchor_y = widget_x, widget_y + widget_h
        elif self._anchor_point == 's':
            anchor_x, anchor_y = widget_x + widget_w // 2, widget_y + widget_h
        elif self._anchor_point == 'se':
            anchor_x, anchor_y = widget_x + widget_w, widget_y + widget_h
        else:
            anchor_x, anchor_y = widget_x, widget_y

        # Use req dimensions — the Toplevel is freshly created and withdrawn;
        # winfo_width/height return the default 200×200 placeholder, not content size.
        w_width = self._toplevel.winfo_reqwidth()
        w_height = self._toplevel.winfo_reqheight()

        x_offset, y_offset = 0, 0
        if window_point == 'nw':
            x_offset, y_offset = 0, 0
        elif window_point == 'n':
            x_offset, y_offset = -w_width // 2, 0
        elif window_point == 'ne':
            x_offset, y_offset = -w_width, 0
        elif window_point == 'w':
            x_offset, y_offset = 0, -w_height // 2
        elif window_point == 'center':
            x_offset, y_offset = -w_width // 2, -w_height // 2
        elif window_point == 'e':
            x_offset, y_offset = -w_width, -w_height // 2
        elif window_point == 'sw':
            x_offset, y_offset = 0, -w_height
        elif window_point == 's':
            x_offset, y_offset = -w_width // 2, -w_height
        elif window_point == 'se':
            x_offset, y_offset = -w_width, -w_height

        # Calculate position with offset
        x = int(anchor_x + x_offset + self._WIDGET_SPACING)
        y = int(anchor_y + y_offset + self._WIDGET_SPACING)

        # Auto-flip logic
        if self._auto_flip:
            vertical_offscreen, horizontal_offscreen = WindowPositioning._check_offscreen(
                self._toplevel, x, y, padding=5
            )

            should_flip_vertical = False
            should_flip_horizontal = False

            if self._auto_flip is True or self._auto_flip == 'vertical':
                should_flip_vertical = vertical_offscreen

            if self._auto_flip is True or self._auto_flip == 'horizontal':
                should_flip_horizontal = horizontal_offscreen

            # Flip if needed
            if should_flip_vertical or should_flip_horizontal:
                flipped_anchor_point = self._anchor_point
                flipped_window_point = window_point

                if should_flip_vertical:
                    flipped_anchor_point = WindowPositioning._flip_anchor_vertical(flipped_anchor_point)
                    flipped_window_point = WindowPositioning._flip_anchor_vertical(flipped_window_point)

                if should_flip_horizontal:
                    flipped_anchor_point = WindowPositioning._flip_anchor_horizontal(flipped_anchor_point)
                    flipped_window_point = WindowPositioning._flip_anchor_horizontal(flipped_window_point)

                # Recalculate anchor coordinates with flipped anchor point
                if flipped_anchor_point == 'nw':
                    anchor_x, anchor_y = widget_x, widget_y
                elif flipped_anchor_point == 'n':
                    anchor_x, anchor_y = widget_x + widget_w // 2, widget_y
                elif flipped_anchor_point == 'ne':
                    anchor_x, anchor_y = widget_x + widget_w, widget_y
                elif flipped_anchor_point == 'w':
                    anchor_x, anchor_y = widget_x, widget_y + widget_h // 2
                elif flipped_anchor_point == 'center':
                    anchor_x, anchor_y = widget_x + widget_w // 2, widget_y + widget_h // 2
                elif flipped_anchor_point == 'e':
                    anchor_x, anchor_y = widget_x + widget_w, widget_y + widget_h // 2
                elif flipped_anchor_point == 'sw':
                    anchor_x, anchor_y = widget_x, widget_y + widget_h
                elif flipped_anchor_point == 's':
                    anchor_x, anchor_y = widget_x + widget_w // 2, widget_y + widget_h
                elif flipped_anchor_point == 'se':
                    anchor_x, anchor_y = widget_x + widget_w, widget_y + widget_h
                else:
                    anchor_x, anchor_y = widget_x, widget_y

                # Recalculate window offset with flipped window point
                if flipped_window_point == 'nw':
                    x_offset, y_offset = 0, 0
                elif flipped_window_point == 'n':
                    x_offset, y_offset = -w_width // 2, 0
                elif flipped_window_point == 'ne':
                    x_offset, y_offset = -w_width, 0
                elif flipped_window_point == 'w':
                    x_offset, y_offset = 0, -w_height // 2
                elif flipped_window_point == 'center':
                    x_offset, y_offset = -w_width // 2, -w_height // 2
                elif flipped_window_point == 'e':
                    x_offset, y_offset = -w_width, -w_height // 2
                elif flipped_window_point == 'sw':
                    x_offset, y_offset = 0, -w_height
                elif flipped_window_point == 's':
                    x_offset, y_offset = -w_width // 2, -w_height
                elif flipped_window_point == 'se':
                    x_offset, y_offset = -w_width, -w_height

                # Recalculate position with flipped anchors
                x = int(anchor_x + x_offset + self._WIDGET_SPACING)
                y = int(anchor_y + y_offset + self._WIDGET_SPACING)

        # Ensure on screen (final safety check)
        try:
            x, y = WindowPositioning.ensure_on_screen(
                self._toplevel, x, y, padding=5, titlebar_height=0
            )
        except Exception:
            pass

        # Set geometry
        self._toplevel.geometry(f"+{x}+{y}")
