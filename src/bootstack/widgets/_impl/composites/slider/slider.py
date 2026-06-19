"""bs.Slider — a themed horizontal or vertical slider widget."""
from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from typing import Any, Callable

from bootstack.widgets._impl.mixins.configure_mixin import ConfigureDelegationMixin, configure_delegate
from bootstack.widgets.types import Master, Orient, AccentToken, SurfaceToken, WidgetState
from bootstack.signals import Signal
from bootstack.events import SliderEvent, SliderCommitEvent
from ._shared import (
    HL, HANDLE_SIZE, TRACK_H,
    BADGE_H, BADGE_PAD_X, BADGE_GAP, BADGE_FONT_SIZE,
    TICK_GAP, MAJOR_TICK_H, MINOR_TICK_H, LABEL_GAP, LABEL_FONT_SIZE,
    STEP, STEP_LARGE,
    _make_badge, _make_handle, _make_track, resolve_colors, get_widget_bg,
)


class Slider(ConfigureDelegationMixin, tk.Frame):
    # Slider manages its own styling and theming; skip autostyle registration
    # for this widget and all tk children created inside it.
    _bs_autostyle = False

    """A themed horizontal or vertical slider widget.

    Replaces `ttk.Scale` with full theming support, optional tick marks,
    value badge, min/max labels, and reactive signal/variable
    binding.

    The current value is accessible via the `value` property, `get()` /
    `set()` methods, `configure(value=x)`, or a bound `variable` /
    `signal`.
    """

    def __init__(
        self,
        master: Master = None,
        *,
        minvalue: float = 0,
        maxvalue: float = 100,
        value: float = 0,
        orient: Orient = "horizontal",
        accent: AccentToken = "primary",
        surface: SurfaceToken = "content",
        variable: tk.DoubleVar | None = None,
        signal: Signal[float] | None = None,
        state: WidgetState = "normal",
        show_value: bool = False,
        show_minmax: bool = False,
        tick_interval: float | None = None,
        minor_ticks: int = 0,
        tick_labels: bool = True,
        tick_format: str = "{:.0f}",
        step: float | None = None,
        **kw: Any,
    ) -> None:
        """Create a Slider widget.

        Args:
            master: Parent widget.
            minvalue: Minimum value of the slider range.
            maxvalue: Maximum value of the slider range.
            value: Initial value. Ignored when `variable` or `signal` is provided.
            orient: Orientation — `'horizontal'` or `'vertical'`.
            accent: Accent token controlling fill, handle, and focus ring color.
            surface: Surface token for trough and background color context.
            variable: Tkinter DoubleVar to bind to the slider value.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            signal: Reactive Signal linked to the slider value.
            state: Widget state — `'normal'` or `'disabled'`.
            show_value: Show a floating badge above (horizontal) or beside
                (vertical) the handle displaying the current value.
            show_minmax: Show `minvalue` and `maxvalue` labels at the
                track ends. Redundant when `tick_interval` is set.
            tick_interval: Spacing between major tick marks. `None` disables ticks.
            minor_ticks: Number of minor tick marks between each major tick.
            tick_labels: Show numeric labels at major tick positions.
            tick_format: Format string for tick and badge labels (e.g. `"{:.1f}°C"`).
            step: Snap increment. When set, click/drag values snap to multiples
                of `step` (measured from `minvalue`) and arrow keys move by `step`.
                `None` leaves the value continuous. Independent of `tick_interval`.
        """
        self._minvalue = float(minvalue)
        self._maxvalue = float(maxvalue)
        self._step_size = float(step) if step else None
        self._kbd_step = self._step_size if self._step_size else float(STEP)
        self._kbd_step_large = self._step_size * 10 if self._step_size else float(STEP_LARGE)
        self._orient = orient
        self._accent = accent
        self._surface = surface
        self._state = state
        self._show_value = show_value
        self._show_minmax = show_minmax
        self._tick_interval = tick_interval
        self._minor_ticks = minor_ticks
        self._tick_labels = tick_labels
        self._tick_format = tick_format

        self._handle_size = HANDLE_SIZE
        self._track_h = TRACK_H

        # Cross-axis allocation (y for horizontal, x for vertical).
        # For vertical sliders the badge sits to the LEFT of the track, so
        # badge_zone must be wide enough for the widest formatted value.
        if show_value:
            if orient == "vertical":
                _bfont = tkfont.Font(family="TkDefaultFont", size=BADGE_FONT_SIZE, weight="bold")
                _bw = max(_bfont.measure(tick_format.format(float(maxvalue))) + BADGE_PAD_X * 2, BADGE_H)
                self._badge_zone = _bw + BADGE_GAP
            else:
                self._badge_zone = BADGE_H + BADGE_GAP
        else:
            self._badge_zone = 0
        self._tick_zone = self._calc_tick_zone()
        cross_size = self._badge_zone + self._handle_size + self._tick_zone

        # Variable / signal binding — always create a Signal so callers get a
        # clean reactive API; derive the tk.DoubleVar from it.
        if signal is not None:
            self._signal: Signal[float] = signal
        elif variable is not None:
            self._signal = Signal(variable.get())
            # Keep the provided variable in sync via trace rather than replacing it
            self._signal.var.trace_add(
                "write", lambda *_: variable.set(self._signal.var.get()))
            variable.trace_add(
                "write", lambda *_: self._signal.var.set(variable.get()))
        else:
            self._signal = Signal(self._snap(float(value)))
        self._var = self._signal.var
        self._prev_value: float = self._var.get()

        # Image refs (prevent GC)
        self._handle_photo: Any = None
        self._track_photo: Any = None

        # Badge geometry (set when show_value=True)
        self._badge_w: int = 0
        self._badge_photo: Any = None

        # Stable canvas width captured in _on_configure — used for badge clamping
        # to break any circular dependency between badge position and frame size.
        self._cw: int = 0

        # Tick canvas item IDs
        self._tick_items: list[int] = []

        kw.setdefault('bd', 0)
        kw.setdefault('relief', 'flat')

        # Resolve theme colors — use parent's actual background so the slider
        # canvas blends with its container surface and the trough is computed
        # against the real surface color, not always #ffffff.
        self._colors = resolve_colors(self._accent, self._surface, get_widget_bg(master))

        # Build frame + canvas
        # highlightcolor starts as bg (invisible); shown only on keyboard focus
        if self._orient == "horizontal":
            super().__init__(
                master,
                width=1,
                height=cross_size + HL * 2,
                takefocus=True,
                highlightthickness=HL,
                highlightcolor=self._colors['bg'],
                highlightbackground=self._colors['bg'],
                **kw,
            )
            self.pack_propagate(False)
            self._canvas = tk.Canvas(
                self, width=1, height=cross_size,
                bd=0, highlightthickness=0, bg=self._colors['bg'],
            )
            self._canvas.place(x=0, y=0, relwidth=1, height=cross_size)
        else:
            super().__init__(
                master,
                width=cross_size + HL * 2,
                height=1,
                takefocus=True,
                highlightthickness=HL,
                highlightcolor=self._colors['bg'],
                highlightbackground=self._colors['bg'],
                **kw,
            )
            self.pack_propagate(False)
            self._canvas = tk.Canvas(
                self, width=cross_size, height=1,
                bd=0, highlightthickness=0, bg=self._colors['bg'],
            )
            self._canvas.place(x=0, y=0, relheight=1, width=cross_size)

        # Center of the track in the cross axis (y for horizontal, x for vertical)
        self._track_center = self._badge_zone + self._handle_size // 2

        # Canvas items — track must be below handle in z-order
        if self._orient == "horizontal":
            self._track_item = self._canvas.create_image(0, self._track_center, anchor="w")
            self._handle_item = self._canvas.create_image(0, self._track_center, anchor="center")
        else:
            self._track_item = self._canvas.create_image(self._track_center, 0, anchor="n")
            self._handle_item = self._canvas.create_image(self._track_center, 0, anchor="center")

        # Badge items — PIL image background + text item on top
        self._badge_item: int | None = None
        self._badge_text_item: int | None = None
        if self._show_value:
            badge_font = tkfont.Font(family="TkDefaultFont", size=BADGE_FONT_SIZE, weight="bold")
            max_text = self._tick_format.format(self._maxvalue)
            self._badge_w = max(badge_font.measure(max_text) + BADGE_PAD_X * 2, BADGE_H)
            self._badge_photo = _make_badge(self._badge_w, BADGE_H, self._colors['badge_bg'])
            self._badge_item = self._canvas.create_image(0, 0, anchor="nw", image=self._badge_photo)
            self._badge_text_item = self._canvas.create_text(
                0, 0, text="", fill=self._colors['badge_text'],
                font=badge_font, anchor="center",
            )

        # Min/max end-labels (only when ticks are not drawn)
        self._minlabel_item: int | None = None
        self._maxlabel_item: int | None = None
        if self._show_minmax and self._tick_interval is None:
            label_font = tkfont.Font(family="TkDefaultFont", size=LABEL_FONT_SIZE)
            if self._orient == "horizontal":
                label_y = self._track_center + self._handle_size // 2 + TICK_GAP + LABEL_GAP
                self._minlabel_item = self._canvas.create_text(
                    0, label_y,
                    text=self._tick_format.format(self._minvalue),
                    fill=self._colors['tick'], font=label_font, anchor="nw",
                )
                self._maxlabel_item = self._canvas.create_text(
                    0, label_y,
                    text=self._tick_format.format(self._maxvalue),
                    fill=self._colors['tick'], font=label_font, anchor="ne",
                )
            else:
                label_x = self._track_center + self._handle_size // 2 + TICK_GAP + LABEL_GAP
                self._minlabel_item = self._canvas.create_text(
                    label_x, 0,
                    text=self._tick_format.format(self._minvalue),
                    fill=self._colors['tick'], font=label_font, anchor="w",
                )
                self._maxlabel_item = self._canvas.create_text(
                    label_x, 0,
                    text=self._tick_format.format(self._maxvalue),
                    fill=self._colors['tick'], font=label_font, anchor="w",
                )

        self._render_handle(self._colors)

        # Keyboard-vs-mouse focus tracking (ring only on Tab navigation)
        self._mouse_pressed = False

        # Input bindings
        self._canvas.bind("<Button-1>", self._on_click)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<Button-1>", self._mouse_focus_set, add=True)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._canvas.tag_bind(self._handle_item, "<Button-1>", self._on_click)
        self._canvas.tag_bind(self._handle_item, "<B1-Motion>", self._on_drag)
        self._canvas.tag_bind(self._handle_item, "<Button-1>", self._mouse_focus_set, add=True)
        self._canvas.tag_bind(self._handle_item, "<ButtonRelease-1>", self._on_release)

        self.bind("<FocusIn>",     self._on_focus_in)
        self.bind("<FocusOut>",    self._on_focus_out)
        self.bind("<Left>",        lambda e: self._step(-self._kbd_step))
        self.bind("<Right>",       lambda e: self._step(+self._kbd_step))
        self.bind("<Down>",        lambda e: self._step(-self._kbd_step))
        self.bind("<Up>",          lambda e: self._step(+self._kbd_step))
        self.bind("<Shift-Left>",  lambda e: self._step(-self._kbd_step_large))
        self.bind("<Shift-Right>", lambda e: self._step(+self._kbd_step_large))
        self.bind("<Home>",        lambda e: self._jump(self._minvalue))
        self.bind("<End>",         lambda e: self._jump(self._maxvalue))
        self._canvas.bind("<Configure>", self._on_configure)

        self._var.trace_add("write", self._on_var_write)
        # Re-resolve the track/handle colors on a theme change. Subscribe to the
        # STD publisher (fires ONCE, after the rebuild) — NOT the ttk
        # `<<ThemeChanged>>`, which re-fires per style reconfigure during the
        # rebuild (×N styles × every slider on screen → thousands of redraws).
        from bootstack._core.publisher import Channel, Publisher
        name = str(self)
        Publisher.subscribe(name=name, func=lambda *_a, **_k: self._on_theme_changed(),
                            channel=Channel.STD)
        self.bind("<Destroy>", lambda e, n=name: Publisher.unsubscribe(n), add="+")
        self.bind("<Map>", lambda e: self._on_map(), add="+")

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _calc_tick_zone(self) -> int:
        if self._tick_interval is not None:
            base = TICK_GAP + MAJOR_TICK_H
            if self._tick_labels:
                if self._orient == "vertical":
                    base += LABEL_GAP + self._measure_max_label_width()
                else:
                    base += LABEL_GAP + LABEL_FONT_SIZE + 4
            return base
        if self._show_minmax:
            if self._orient == "vertical":
                return TICK_GAP + LABEL_GAP + self._measure_max_label_width()
            return TICK_GAP + LABEL_GAP + LABEL_FONT_SIZE + 4
        return 0

    def _measure_max_label_width(self) -> int:
        """Return pixel width of the widest tick/minmax label."""
        font = tkfont.Font(family="TkDefaultFont", size=LABEL_FONT_SIZE)
        candidates = [self._tick_format.format(self._minvalue),
                      self._tick_format.format(self._maxvalue)]
        return max(font.measure(t) for t in candidates) + 4

    def _track_range(self) -> tuple[int, int]:
        """Return (start, end) handle travel range in canvas coords (main axis)."""
        half = self._handle_size // 2
        if self._orient == "horizontal":
            # _cw is the canvas's exact allocated width (from canvas <Configure>).
            # Subtract an extra pixel so the handle image (half px on each side)
            # never reaches the canvas boundary.
            w = self._cw if self._cw > 0 else max(1, self._canvas.winfo_width())
            return half, max(half + 1, w - half - 1)
        else:
            h = self.winfo_height() - 2 * HL
            return half, max(half + 1, h - half - 1)

    def _value_to_pos(self, val: float) -> int:
        """Map a value to a canvas pixel position along the main axis."""
        start, end = self._track_range()
        span = self._maxvalue - self._minvalue
        if span == 0:
            return start
        ratio = max(0.0, min(1.0, (val - self._minvalue) / span))
        if self._orient == "vertical":
            ratio = 1.0 - ratio  # vertical: top = max, bottom = min
        return start + int(ratio * (end - start))

    def _pos_to_value(self, pos: int) -> float:
        """Map a canvas pixel position to a slider value."""
        start, end = self._track_range()
        if end == start:
            return self._minvalue
        ratio = max(0.0, min(1.0, (pos - start) / (end - start)))
        if self._orient == "vertical":
            ratio = 1.0 - ratio
        return self._minvalue + ratio * (self._maxvalue - self._minvalue)

    def _snap(self, v: float) -> float:
        """Clamp `v` to [min, max] and, when `step` is set, snap it to the
        nearest grid point (measured from `minvalue`). `maxvalue` stays reachable
        even when the range is not an exact multiple of `step`."""
        v = max(self._minvalue, min(self._maxvalue, float(v)))
        if not self._step_size:
            return v
        grid = self._minvalue + round((v - self._minvalue) / self._step_size) * self._step_size
        grid = max(self._minvalue, min(self._maxvalue, grid))
        # Let the exact maximum win when the value is closer to it than to the
        # last grid point (an off-grid max would otherwise be unreachable).
        if abs(v - self._maxvalue) < abs(v - grid):
            return self._maxvalue
        return grid

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def _render_handle(self, colors: dict[str, str]) -> None:
        fill = colors['handle_disabled'] if self._state == "disabled" else colors['handle']
        self._handle_photo = _make_handle(fill, colors['ring'], colors['handle_border'])
        self._canvas.itemconfig(self._handle_item, image=self._handle_photo)

    def _update_badge_colors(self, colors: dict[str, str]) -> None:
        if self._badge_item is not None:
            self._badge_photo = _make_badge(self._badge_w, BADGE_H, colors['badge_bg'])
            self._canvas.itemconfig(self._badge_item, image=self._badge_photo)
        if self._badge_text_item is not None:
            self._canvas.itemconfig(self._badge_text_item, fill=colors['badge_text'])

    # ------------------------------------------------------------------
    # Sync: value → visual
    # ------------------------------------------------------------------

    def _sync(self) -> None:
        val = self._var.get()
        pos = self._value_to_pos(val)
        start, end = self._track_range()
        track_len = end - start

        fill_c = self._colors['fill_disabled'] if self._state == "disabled" else self._colors['fill']

        if self._orient == "horizontal":
            fill_px = pos - start
            photo = _make_track(track_len, self._track_h, 0, fill_px,
                                self._colors['trough'], fill_c)
            if photo:
                self._track_photo = photo
                self._canvas.coords(self._track_item, start, self._track_center)
                self._canvas.itemconfig(self._track_item, image=self._track_photo)
            self._canvas.coords(self._handle_item, pos, self._track_center)
            if self._show_value:
                self._update_badge_h(pos, val)
            if self._show_minmax and self._tick_interval is None:
                label_y = self._track_center + self._handle_size // 2 + TICK_GAP + LABEL_GAP
                self._canvas.coords(self._minlabel_item, start, label_y)
                self._canvas.coords(self._maxlabel_item, end, label_y)
        else:
            # Vertical: bottom = min, top = max.  fill_px = pixels from bottom.
            fill_px = end - pos
            photo = _make_track(track_len, self._track_h, 0, fill_px,
                                self._colors['trough'], fill_c,
                                vertical=True)
            if photo:
                self._track_photo = photo
                # After rotate(90), image is track_h wide × track_len tall; anchor "n"
                self._canvas.coords(self._track_item, self._track_center, start)
                self._canvas.itemconfig(self._track_item, image=self._track_photo)
            self._canvas.coords(self._handle_item, self._track_center, pos)
            if self._show_value:
                self._update_badge_v(pos, val)
            if self._show_minmax and self._tick_interval is None:
                label_x = self._track_center + self._handle_size // 2 + TICK_GAP + LABEL_GAP
                self._canvas.coords(self._minlabel_item, label_x, end)
                self._canvas.coords(self._maxlabel_item, label_x, start)

    def _update_badge_h(self, handle_x: int, val: float) -> None:
        if self._badge_item is None:
            return
        bw = self._badge_w
        # Use stable _cw captured in _on_configure; fall back to live query only if
        # _on_configure has not fired yet (widget not yet laid out).
        cw = self._cw if self._cw > 0 else max(1, self.winfo_width() - 2 * HL)
        # Clamp so image occupies [badge_x, badge_x+bw-1] ⊆ [0, cw-1].
        badge_x = max(0, min(handle_x - bw // 2, cw - bw))
        badge_y = self._badge_zone - BADGE_H - 2
        self._canvas.coords(self._badge_item, badge_x, badge_y)
        if self._badge_text_item is not None:
            self._canvas.coords(self._badge_text_item, badge_x + bw // 2, badge_y + BADGE_H // 2)
            self._canvas.itemconfig(self._badge_text_item, text=self._tick_format.format(val))

    def _update_badge_v(self, handle_y: int, val: float) -> None:
        if self._badge_item is None:
            return
        bw = self._badge_w
        ch = self.winfo_height() - 2 * HL
        badge_x = self._badge_zone - bw - 2
        badge_y = max(0, min(handle_y - BADGE_H // 2, ch - BADGE_H))
        self._canvas.coords(self._badge_item, badge_x, badge_y)
        if self._badge_text_item is not None:
            self._canvas.coords(self._badge_text_item, badge_x + bw // 2, badge_y + BADGE_H // 2)
            self._canvas.itemconfig(self._badge_text_item, text=self._tick_format.format(val))

    # ------------------------------------------------------------------
    # Tick marks
    # ------------------------------------------------------------------

    def _setup_ticks(self) -> None:
        if self._tick_interval is None:
            return
        for item in self._tick_items:
            self._canvas.delete(item)
        self._tick_items.clear()

        tick_color = self._colors['tick']
        font = tkfont.Font(family="TkDefaultFont", size=LABEL_FONT_SIZE)
        start, end = self._track_range()
        span = self._maxvalue - self._minvalue
        if span <= 0:
            return

        if self._orient == "horizontal":
            major_y0 = self._track_center + self._handle_size // 2 + TICK_GAP
            major_y1 = major_y0 + MAJOR_TICK_H
            minor_y1 = major_y0 + MINOR_TICK_H
            label_y = major_y1 + LABEL_GAP

            val = self._minvalue
            while val <= self._maxvalue + 1e-9:
                x = self._value_to_pos(val)
                self._tick_items.append(
                    self._canvas.create_line(x, major_y0, x, major_y1, fill=tick_color, width=1))
                if self._tick_labels:
                    self._tick_items.append(
                        self._canvas.create_text(x, label_y, text=self._tick_format.format(val),
                                                 fill=tick_color, font=font, anchor="n"))
                if self._minor_ticks > 0:
                    minor_step = self._tick_interval / (self._minor_ticks + 1)
                    for i in range(1, self._minor_ticks + 1):
                        mv = val + i * minor_step
                        if mv >= self._maxvalue - 1e-9:
                            break
                        mx = self._value_to_pos(mv)
                        self._tick_items.append(
                            self._canvas.create_line(mx, major_y0, mx, minor_y1,
                                                     fill=tick_color, width=1))
                val += self._tick_interval
        else:
            major_x0 = self._track_center + self._handle_size // 2 + TICK_GAP
            major_x1 = major_x0 + MAJOR_TICK_H
            minor_x1 = major_x0 + MINOR_TICK_H
            label_x = major_x1 + LABEL_GAP

            val = self._minvalue
            while val <= self._maxvalue + 1e-9:
                y = self._value_to_pos(val)
                self._tick_items.append(
                    self._canvas.create_line(major_x0, y, major_x1, y, fill=tick_color, width=1))
                if self._tick_labels:
                    self._tick_items.append(
                        self._canvas.create_text(label_x, y, text=self._tick_format.format(val),
                                                 fill=tick_color, font=font, anchor="w"))
                if self._minor_ticks > 0:
                    minor_step = self._tick_interval / (self._minor_ticks + 1)
                    for i in range(1, self._minor_ticks + 1):
                        mv = val + i * minor_step
                        if mv >= self._maxvalue - 1e-9:
                            break
                        my = self._value_to_pos(mv)
                        self._tick_items.append(
                            self._canvas.create_line(major_x0, my, minor_x1, my,
                                                     fill=tick_color, width=1))
                val += self._tick_interval

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_configure(self, event: tk.Event) -> None:
        # Bound to canvas <Configure>, so event.width/height IS the canvas size —
        # no border arithmetic needed.
        if self._orient == "horizontal" and event.width > self._handle_size:
            self._cw = event.width
            self._canvas.configure(scrollregion=(0, 0, event.width, event.height))
            self._setup_ticks()
            self._sync()
        elif self._orient == "vertical" and event.height > self._handle_size:
            self._canvas.configure(scrollregion=(0, 0, event.width, event.height))
            self._setup_ticks()
            self._sync()

    def _on_var_write(self, *_: Any) -> None:
        self._sync()
        val = self._var.get()
        self.event_generate("<<Change>>", data=SliderEvent(value=val, prev_value=self._prev_value))
        self._prev_value = val

    def _mouse_focus_set(self, _event: tk.Event) -> None:
        self._mouse_pressed = True
        self.focus_set()

    def _on_focus_in(self, _event: tk.Event) -> None:
        if self._mouse_pressed:
            self._mouse_pressed = False
            return
        self.configure(highlightcolor=self._colors['focus'])

    def _on_focus_out(self, _event: tk.Event) -> None:
        self.configure(highlightcolor=self._colors['bg'])

    def _on_click(self, event: tk.Event) -> None:
        if self._state == "disabled":
            return
        # event.x/y are already in canvas coordinates — no winfo_x/y offset needed.
        if self._orient == "horizontal":
            self._var.set(self._snap(self._pos_to_value(event.x)))
        else:
            self._var.set(self._snap(self._pos_to_value(event.y)))

    def _on_drag(self, event: tk.Event) -> None:
        self._on_click(event)

    def _on_release(self, event: tk.Event) -> None:
        if self._state == "disabled":
            return
        val = self._var.get()
        self.event_generate("<<Commit>>", data=SliderCommitEvent(value=val))

    def _step(self, amount: float) -> None:
        if self._state == "disabled":
            return
        new = self._snap(self._var.get() + amount)
        self._var.set(new)
        self.event_generate("<<Commit>>", data=SliderCommitEvent(value=new))

    def _jump(self, value: float) -> None:
        """Keyboard jump (Home/End) — set then commit, like _step does."""
        if self._state == "disabled":
            return
        new = max(self._minvalue, min(self._maxvalue, float(value)))
        self._var.set(new)
        self.event_generate("<<Commit>>", data=SliderCommitEvent(value=new))

    def _reclamp(self) -> None:
        """Pull the current value back into [min, max] (and onto the step grid)
        after a range or step change."""
        cur = self._var.get()
        clamped = self._snap(cur)
        if clamped != cur:
            self._var.set(clamped)   # trace fires _sync + <<Change>>
        else:
            self._sync()

    def _on_map(self) -> None:
        if getattr(self, '_theme_update_pending', False):
            self._on_theme_changed()

    def _on_theme_changed(self) -> None:
        if not self.winfo_viewable():
            self._theme_update_pending = True
            return
        self._theme_update_pending = False
        self._colors = resolve_colors(self._accent, self._surface, get_widget_bg(self.master))
        colors = self._colors
        self.configure(
            highlightbackground=colors['bg'],
            highlightcolor=colors['bg'],  # reset to hidden; re-shown on next keyboard focus
        )
        self._canvas.configure(bg=colors['bg'])
        self._render_handle(colors)
        self._update_badge_colors(colors)
        if self._minlabel_item is not None:
            self._canvas.itemconfig(self._minlabel_item, fill=colors['tick'])
        if self._maxlabel_item is not None:
            self._canvas.itemconfig(self._maxlabel_item, fill=colors['tick'])
        self._setup_ticks()
        self._sync()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def signal(self) -> Signal[float]:
        """Reactive Signal linked to the slider value."""
        return self._signal

    @property
    def value(self) -> float:
        """Current slider value."""
        return self._var.get()

    def get(self) -> float:
        """Return the current slider value."""
        return self._var.get()

    def set(self, value: float) -> None:
        """Set the slider to a new value, clamped to [minvalue, maxvalue] and
        snapped to the step grid when `step` is set.

        Args:
            value: New value to set.
        """
        self._var.set(self._snap(float(value)))

    def on_changed(self, callback: Callable[[SliderEvent], None]) -> str:
        """Register a callback for `<<Change>>` events.

        Args:
            callback: Called with a Tkinter event; `event.value` is
                the current value and `event.prev_value` is the
                value before the change.

        Returns:
            Bind ID — pass to `off_changed()` to unsubscribe.
        """
        return self.bind("<<Change>>", callback, add="+")

    def off_changed(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Change>>`.

        Args:
            bind_id: ID returned by `on_changed()`. If None, removes all.
        """
        self.unbind("<<Change>>", bind_id)

    def on_commit(self, callback: Callable[[SliderCommitEvent], None]) -> str:
        """Register a callback for `<<Commit>>` events.

        Fires on mouse release and keyboard commit, not continuously during drag.
        Use for expensive downstream operations.

        Args:
            callback: Called with a Tkinter event; `event.value` is
                the committed value.

        Returns:
            Bind ID — pass to `off_commit()` to unsubscribe.
        """
        return self.bind("<<Commit>>", callback, add="+")

    def off_commit(self, bind_id: str | None = None) -> None:
        """Unsubscribe from `<<Commit>>`.

        Args:
            bind_id: ID returned by `on_commit()`. If None, removes all.
        """
        self.unbind("<<Commit>>", bind_id)

    @property
    def variable(self) -> tk.DoubleVar:
        """Underlying Tkinter DoubleVar.

        See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
        """
        return self._var

    # ------------------------------------------------------------------
    # Configure delegates
    # ------------------------------------------------------------------

    @configure_delegate('value')
    def _delegate_value(self, value=None):
        if value is None:
            return self._var.get()
        self.set(value)

    @configure_delegate('minvalue')
    def _delegate_minvalue(self, value=None):
        if value is None:
            return self._minvalue
        self._minvalue = float(value)
        self._setup_ticks()
        self._reclamp()

    @configure_delegate('maxvalue')
    def _delegate_maxvalue(self, value=None):
        if value is None:
            return self._maxvalue
        self._maxvalue = float(value)
        self._setup_ticks()
        self._reclamp()

    @configure_delegate('step')
    def _delegate_step(self, value=None):
        if value is None:
            return self._step_size
        self._step_size = float(value) if value else None
        self._kbd_step = self._step_size if self._step_size else float(STEP)
        self._kbd_step_large = self._step_size * 10 if self._step_size else float(STEP_LARGE)
        self._reclamp()   # re-snap the current value onto the new grid

    @configure_delegate('accent')
    def _delegate_accent(self, value=None):
        if value is None:
            return self._accent
        self._accent = value
        self._on_theme_changed()

    @configure_delegate('state')
    def _delegate_state(self, value=None):
        if value is None:
            return self._state
        self._state = value
        self._render_handle(self._colors)
        self._sync()

    @configure_delegate('tick_format')
    def _delegate_tick_format(self, value=None):
        if value is None:
            return self._tick_format
        self._tick_format = value
        self._setup_ticks()
        self._sync()

    @configure_delegate('tick_interval')
    def _delegate_tick_interval(self, value=None):
        if value is None:
            return self._tick_interval
        self._tick_interval = value
        self._setup_ticks()

    @configure_delegate('show_value')
    def _delegate_show_value(self, value=None):
        if value is None:
            return self._show_value
        # show_value creates/destroys canvas items; must be set at construction time.

    @configure_delegate('minor_ticks')
    def _delegate_minor_ticks(self, value=None):
        if value is None:
            return self._minor_ticks
        self._minor_ticks = int(value)
        self._setup_ticks()

    @configure_delegate('tick_labels')
    def _delegate_tick_labels(self, value=None):
        if value is None:
            return self._tick_labels
        self._tick_labels = bool(value)
        self._setup_ticks()

    @configure_delegate('surface')
    def _delegate_surface(self, value=None):
        if value is None:
            return self._surface
        self._surface = value
        self._on_theme_changed()
