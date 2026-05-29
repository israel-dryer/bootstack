"""bs.RangeSlider — a themed two-handle range slider widget."""
from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from typing import Any, Callable

from bootstack.widgets._impl.mixins.configure_mixin import ConfigureDelegationMixin, configure_delegate
from bootstack.widgets.types import Master, Orient, AccentToken, SurfaceToken, WidgetState
from bootstack.signals import Signal
from ._shared import (
    HL, HANDLE_SIZE, TRACK_H,
    BADGE_H, BADGE_PAD_X, BADGE_GAP, BADGE_FONT_SIZE,
    TICK_GAP, MAJOR_TICK_H, MINOR_TICK_H, LABEL_GAP, LABEL_FONT_SIZE,
    STEP, STEP_LARGE, RangeSliderEventData, RangeSliderCommitEventData,
    _make_badge, _make_handle, _make_track, resolve_colors, get_widget_bg,
)


class RangeSlider(ConfigureDelegationMixin, tk.Frame):
    _bs_autostyle = False

    """A themed two-handle range slider widget.

    Provides a low-value and high-value handle that define a selected range
    within ``[minvalue, maxvalue]``.  Both handles are keyboard-accessible
    and cycle with ``Tab``.

    Current range is accessible via ``lovalue`` / ``hivalue`` properties,
    ``get_lo()`` / ``get_hi()`` / ``set_lo()`` / ``set_hi()`` methods, or
    bound ``lo_variable`` / ``hi_variable`` / ``lo_signal`` / ``hi_signal``.
    """

    def __init__(
        self,
        master: Master = None,
        *,
        minvalue: float = 0,
        maxvalue: float = 100,
        lovalue: float = 0,
        hivalue: float = 100,
        orient: Orient = "horizontal",
        accent: AccentToken = "primary",
        surface: SurfaceToken = "content",
        lo_variable: tk.DoubleVar | None = None,
        hi_variable: tk.DoubleVar | None = None,
        lo_signal: Signal[float] | None = None,
        hi_signal: Signal[float] | None = None,
        state: WidgetState = "normal",
        show_value: bool = False,
        tick_interval: float | None = None,
        minor_ticks: int = 0,
        tick_labels: bool = True,
        tick_format: str = "{:.0f}",
        **kw: Any,
    ) -> None:
        """Create a RangeSlider widget.

        Args:
            master: Parent widget.
            minvalue: Minimum bound of the slider range.
            maxvalue: Maximum bound of the slider range.
            lovalue: Initial low-handle value. Ignored when ``lo_variable``
                or ``lo_signal`` is provided.
            hivalue: Initial high-handle value. Ignored when ``hi_variable``
                or ``hi_signal`` is provided.
            orient: Orientation — ``'horizontal'`` or ``'vertical'``.
            accent: Accent token controlling fill, handles, and focus ring color.
            surface: Surface token for trough and background color context.
            lo_variable: Tkinter DoubleVar bound to the low-handle value.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            hi_variable: Tkinter DoubleVar bound to the high-handle value.
                See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
            lo_signal: Reactive Signal linked to the low-handle value.
            hi_signal: Reactive Signal linked to the high-handle value.
            state: Widget state — ``'normal'`` or ``'disabled'``.
            show_value: Show floating badges above/beside each handle displaying
                their current values.
            tick_interval: Spacing between major tick marks. ``None`` disables ticks.
            minor_ticks: Number of minor tick marks between each major tick.
            tick_labels: Show numeric labels at major tick positions.
            tick_format: Format string for tick and badge labels (e.g. ``"{:.1f}°C"``).
        """
        self._minvalue = float(minvalue)
        self._maxvalue = float(maxvalue)
        self._orient = orient
        self._accent = accent
        self._surface = surface
        self._state = state
        self._show_value = show_value
        self._tick_interval = tick_interval
        self._minor_ticks = minor_ticks
        self._tick_labels = tick_labels
        self._tick_format = tick_format

        self._handle_size = HANDLE_SIZE
        self._track_h = TRACK_H

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

        # Variable / signal binding for lo and hi — always create a Signal so
        # callers get a clean reactive API; derive the tk.DoubleVar from it.
        if lo_signal is not None:
            self._lo_signal: Signal[float] = lo_signal
        elif lo_variable is not None:
            self._lo_signal = Signal(lo_variable.get())
            self._lo_signal.var.trace_add(
                "write", lambda *_: lo_variable.set(self._lo_signal.var.get()))
            lo_variable.trace_add(
                "write", lambda *_: self._lo_signal.var.set(lo_variable.get()))
        else:
            self._lo_signal = Signal(float(lovalue))
        self._lo_var = self._lo_signal.var

        if hi_signal is not None:
            self._hi_signal: Signal[float] = hi_signal
        elif hi_variable is not None:
            self._hi_signal = Signal(hi_variable.get())
            self._hi_signal.var.trace_add(
                "write", lambda *_: hi_variable.set(self._hi_signal.var.get()))
            hi_variable.trace_add(
                "write", lambda *_: self._hi_signal.var.set(hi_variable.get()))
        else:
            self._hi_signal = Signal(float(hivalue))
        self._hi_var = self._hi_signal.var

        self._prev_lovalue: float = self._lo_var.get()
        self._prev_hivalue: float = self._hi_var.get()

        # Image refs (prevent GC)
        self._handle_lo_photo: Any = None
        self._handle_hi_photo: Any = None
        self._track_photo: Any = None

        # Badge geometry (set when show_value=True)
        self._badge_w: int = 0
        self._badge_lo_photo: Any = None
        self._badge_hi_photo: Any = None

        # Stable canvas width captured in _on_configure — used for badge clamping.
        self._cw: int = 0

        self._tick_items: list[int] = []

        # Drag / keyboard focus state
        self._dragging: str | None = None   # "lo" | "hi" | None
        self._focus_handle = "lo"

        kw.setdefault('bd', 0)
        kw.setdefault('relief', 'flat')

        self._colors = resolve_colors(self._accent, self._surface, get_widget_bg(master))

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

        self._track_center = self._badge_zone + self._handle_size // 2

        if self._orient == "horizontal":
            self._track_item = self._canvas.create_image(0, self._track_center, anchor="w")
            self._handle_lo_item = self._canvas.create_image(0, self._track_center, anchor="center")
            self._handle_hi_item = self._canvas.create_image(0, self._track_center, anchor="center")
        else:
            self._track_item = self._canvas.create_image(self._track_center, 0, anchor="n")
            self._handle_lo_item = self._canvas.create_image(self._track_center, 0, anchor="center")
            self._handle_hi_item = self._canvas.create_image(self._track_center, 0, anchor="center")

        # Badge items — PIL image background + text items on top
        self._badge_lo_item: int | None = None
        self._badge_hi_item: int | None = None
        self._badge_lo_text: int | None = None
        self._badge_hi_text: int | None = None
        if self._show_value:
            badge_font = tkfont.Font(family="TkDefaultFont", size=BADGE_FONT_SIZE, weight="bold")
            max_text = self._tick_format.format(self._maxvalue)
            self._badge_w = max(badge_font.measure(max_text) + BADGE_PAD_X * 2, BADGE_H)
            _bg = self._colors['badge_bg']
            self._badge_lo_photo = _make_badge(self._badge_w, BADGE_H, _bg)
            self._badge_hi_photo = _make_badge(self._badge_w, BADGE_H, _bg)
            self._badge_lo_item = self._canvas.create_image(0, 0, anchor="nw", image=self._badge_lo_photo)
            self._badge_hi_item = self._canvas.create_image(0, 0, anchor="nw", image=self._badge_hi_photo)
            self._badge_lo_text = self._canvas.create_text(
                0, 0, text="", fill=self._colors['badge_text'],
                font=badge_font, anchor="center",
            )
            self._badge_hi_text = self._canvas.create_text(
                0, 0, text="", fill=self._colors['badge_text'],
                font=badge_font, anchor="center",
            )

        self._render_handles(self._colors)

        # Keyboard-vs-mouse focus tracking (ring only on Tab navigation)
        self._mouse_pressed = False

        # Canvas-level click: pick nearest handle
        self._canvas.bind("<Button-1>", self._on_canvas_click)
        self._canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self._canvas.bind("<Button-1>", self._mouse_focus_set, add=True)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)

        # Per-handle drag bindings
        self._canvas.tag_bind(self._handle_lo_item, "<Button-1>",
                               lambda e: self._handle_press(e, "lo"))
        self._canvas.tag_bind(self._handle_lo_item, "<B1-Motion>", self._on_handle_drag)
        self._canvas.tag_bind(self._handle_lo_item, "<ButtonRelease-1>", self._on_release)
        self._canvas.tag_bind(self._handle_hi_item, "<Button-1>",
                               lambda e: self._handle_press(e, "hi"))
        self._canvas.tag_bind(self._handle_hi_item, "<B1-Motion>", self._on_handle_drag)
        self._canvas.tag_bind(self._handle_hi_item, "<ButtonRelease-1>", self._on_release)

        self.bind("<FocusIn>",     self._on_focus_in)
        self.bind("<FocusOut>",    self._on_focus_out)
        self.bind("<Left>",        lambda e: self._step(-STEP))
        self.bind("<Right>",       lambda e: self._step(+STEP))
        self.bind("<Down>",        lambda e: self._step(-STEP))
        self.bind("<Up>",          lambda e: self._step(+STEP))
        self.bind("<Shift-Left>",  lambda e: self._step(-STEP_LARGE))
        self.bind("<Shift-Right>", lambda e: self._step(+STEP_LARGE))
        self.bind("<Home>",        lambda e: self._set_focused(self._minvalue))
        self.bind("<End>",         lambda e: self._set_focused(self._maxvalue))
        self.bind("<Tab>",         self._cycle_handle)
        self._canvas.bind("<Configure>", self._on_configure)

        self._lo_var.trace_add("write", self._on_lo_write)
        self._hi_var.trace_add("write", self._on_hi_write)
        root = self.nametowidget(".")
        _tid = root.bind("<<ThemeChanged>>", lambda e: self._on_theme_changed(), add="+")
        self.bind("<Destroy>", lambda e, r=root, b=_tid: r.unbind("<<ThemeChanged>>", b), add="+")
        self.bind("<Map>", lambda e: self._on_map(), add="+")

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _calc_tick_zone(self) -> int:
        if self._tick_interval is None:
            return 0
        base = TICK_GAP + MAJOR_TICK_H
        if self._tick_labels:
            if self._orient == "vertical":
                base += LABEL_GAP + self._measure_max_label_width()
            else:
                base += LABEL_GAP + LABEL_FONT_SIZE + 4
        return base

    def _measure_max_label_width(self) -> int:
        font = tkfont.Font(family="TkDefaultFont", size=LABEL_FONT_SIZE)
        candidates = [self._tick_format.format(self._minvalue),
                      self._tick_format.format(self._maxvalue)]
        return max(font.measure(t) for t in candidates) + 4

    def _track_range(self) -> tuple[int, int]:
        half = self._handle_size // 2
        if self._orient == "horizontal":
            w = self._cw if self._cw > 0 else max(1, self._canvas.winfo_width())
            return half, max(half + 1, w - half - 1)
        else:
            h = self.winfo_height() - 2 * HL
            return half, max(half + 1, h - half - 1)

    def _value_to_pos(self, val: float) -> int:
        start, end = self._track_range()
        span = self._maxvalue - self._minvalue
        if span == 0:
            return start
        ratio = max(0.0, min(1.0, (val - self._minvalue) / span))
        if self._orient == "vertical":
            ratio = 1.0 - ratio
        return start + int(ratio * (end - start))

    def _pos_to_value(self, pos: int) -> float:
        start, end = self._track_range()
        if end == start:
            return self._minvalue
        ratio = max(0.0, min(1.0, (pos - start) / (end - start)))
        if self._orient == "vertical":
            ratio = 1.0 - ratio
        return self._minvalue + ratio * (self._maxvalue - self._minvalue)

    def _event_pos(self, event: tk.Event) -> int:
        # event.x/y are already in canvas coordinates.
        if self._orient == "horizontal":
            return event.x
        return event.y

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def _render_handles(self, colors: dict[str, str]) -> None:
        fill = colors['handle_disabled'] if self._state == "disabled" else colors['handle']
        self._handle_lo_photo = _make_handle(fill, colors['ring'], colors['handle_border'])
        self._handle_hi_photo = _make_handle(fill, colors['ring'], colors['handle_border'])
        self._canvas.itemconfig(self._handle_lo_item, image=self._handle_lo_photo)
        self._canvas.itemconfig(self._handle_hi_item, image=self._handle_hi_photo)

    def _update_badge_colors(self, colors: dict[str, str]) -> None:
        bg = colors['badge_bg']
        if self._badge_lo_item is not None:
            self._badge_lo_photo = _make_badge(self._badge_w, BADGE_H, bg)
            self._canvas.itemconfig(self._badge_lo_item, image=self._badge_lo_photo)
        if self._badge_hi_item is not None:
            self._badge_hi_photo = _make_badge(self._badge_w, BADGE_H, bg)
            self._canvas.itemconfig(self._badge_hi_item, image=self._badge_hi_photo)
        for item in (self._badge_lo_text, self._badge_hi_text):
            if item is not None:
                self._canvas.itemconfig(item, fill=colors['badge_text'])

    # ------------------------------------------------------------------
    # Sync: values → visual
    # ------------------------------------------------------------------

    def _sync(self) -> None:
        lo_val = self._lo_var.get()
        hi_val = self._hi_var.get()
        lo_pos = self._value_to_pos(lo_val)
        hi_pos = self._value_to_pos(hi_val)
        start, end = self._track_range()
        track_len = end - start

        fill_c = self._colors['fill_disabled'] if self._state == "disabled" else self._colors['fill']

        if self._orient == "horizontal":
            fill_start = lo_pos - start
            fill_end = hi_pos - start
            photo = _make_track(track_len, self._track_h, fill_start, fill_end,
                                self._colors['trough'], fill_c)
            if photo:
                self._track_photo = photo
                self._canvas.coords(self._track_item, start, self._track_center)
                self._canvas.itemconfig(self._track_item, image=self._track_photo)
            self._canvas.coords(self._handle_lo_item, lo_pos, self._track_center)
            self._canvas.coords(self._handle_hi_item, hi_pos, self._track_center)
            if self._show_value:
                self._update_badges_h(lo_pos, hi_pos, lo_val, hi_val)
        else:
            # Vertical: top = max (small canvas y), bottom = min (large canvas y).
            # lo_pos >= hi_pos in canvas coords (lower value → lower y-pos → larger canvas y).
            # PIL rotate(90) is CCW: LEFT of horizontal → BOTTOM of vertical,
            #                        RIGHT of horizontal → TOP of vertical.
            # So to fill from canvas y=hi_pos (top) to canvas y=lo_pos (bottom):
            #   fill_start = end - lo_pos  (maps to bottom of fill region)
            #   fill_end   = end - hi_pos  (maps to top of fill region)
            fill_start = max(0, end - lo_pos)
            fill_end = min(track_len, end - hi_pos)
            photo = _make_track(track_len, self._track_h, fill_start, fill_end,
                                self._colors['trough'], fill_c,
                                vertical=True)
            if photo:
                self._track_photo = photo
                self._canvas.coords(self._track_item, self._track_center, start)
                self._canvas.itemconfig(self._track_item, image=self._track_photo)
            self._canvas.coords(self._handle_lo_item, self._track_center, lo_pos)
            self._canvas.coords(self._handle_hi_item, self._track_center, hi_pos)
            if self._show_value:
                self._update_badges_v(lo_pos, hi_pos, lo_val, hi_val)

    def _update_badges_h(self, lo_x: int, hi_x: int, lo_val: float, hi_val: float) -> None:
        if self._badge_lo_item is None:
            return
        bw = self._badge_w
        cw = self._cw if self._cw > 0 else max(1, self.winfo_width() - 2 * HL)
        badge_y = self._badge_zone - BADGE_H - 2
        # Clamp so image occupies [bx, bx+bw-1] ⊆ [0, cw-1].
        lo_bx = max(0, min(lo_x - bw // 2, cw - bw))
        hi_bx = max(0, min(hi_x - bw // 2, cw - bw))
        for img_item, text_item, bx, val in (
            (self._badge_lo_item, self._badge_lo_text, lo_bx, lo_val),
            (self._badge_hi_item, self._badge_hi_text, hi_bx, hi_val),
        ):
            self._canvas.coords(img_item, bx, badge_y)
            if text_item is not None:
                self._canvas.coords(text_item, bx + bw // 2, badge_y + BADGE_H // 2)
                self._canvas.itemconfig(text_item, text=self._tick_format.format(val))

    def _update_badges_v(self, lo_y: int, hi_y: int, lo_val: float, hi_val: float) -> None:
        if self._badge_lo_item is None:
            return
        bw = self._badge_w
        ch = self.winfo_height() - 2 * HL
        badge_x = self._badge_zone - bw - 2
        for img_item, text_item, by_center, val in (
            (self._badge_lo_item, self._badge_lo_text, lo_y, lo_val),
            (self._badge_hi_item, self._badge_hi_text, hi_y, hi_val),
        ):
            badge_y = max(0, min(by_center - BADGE_H // 2, ch - BADGE_H))
            self._canvas.coords(img_item, badge_x, badge_y)
            if text_item is not None:
                self._canvas.coords(text_item, badge_x + bw // 2, badge_y + BADGE_H // 2)
                self._canvas.itemconfig(text_item, text=self._tick_format.format(val))

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
        if self._orient == "horizontal" and event.width > self._handle_size:
            self._cw = event.width
            self._canvas.configure(scrollregion=(0, 0, event.width, event.height))
            self._setup_ticks()
            self._sync()
        elif self._orient == "vertical" and event.height > self._handle_size:
            self._canvas.configure(scrollregion=(0, 0, event.width, event.height))
            self._setup_ticks()
            self._sync()

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

    def _on_canvas_click(self, event: tk.Event) -> None:
        if self._state == "disabled":
            return
        pos = self._event_pos(event)
        lo_pos = self._value_to_pos(self._lo_var.get())
        hi_pos = self._value_to_pos(self._hi_var.get())
        self._dragging = "lo" if abs(pos - lo_pos) <= abs(pos - hi_pos) else "hi"
        self._focus_handle = self._dragging
        self._move(pos)

    def _on_canvas_drag(self, event: tk.Event) -> None:
        if self._state == "disabled":
            return
        self._move(self._event_pos(event))

    def _handle_press(self, event: tk.Event, which: str) -> None:
        if self._state == "disabled":
            return
        self._dragging = which
        self._focus_handle = which
        self.focus_set()

    def _on_handle_drag(self, event: tk.Event) -> None:
        if self._state == "disabled" or self._dragging is None:
            return
        self._move(self._event_pos(event))

    def _on_release(self, event: tk.Event) -> None:
        if self._state == "disabled":
            return
        self._dragging = None
        self.event_generate("<<Commit>>", data={
            "lovalue": self._lo_var.get(),
            "hivalue": self._hi_var.get(),
        })

    def _move(self, pos: int) -> None:
        value = self._pos_to_value(pos)
        if self._dragging == "lo":
            self._lo_var.set(max(self._minvalue, min(value, self._hi_var.get())))
        else:
            self._hi_var.set(min(self._maxvalue, max(value, self._lo_var.get())))

    def _step(self, amount: float) -> None:
        if self._state == "disabled":
            return
        self._set_focused(
            (self._lo_var.get() if self._focus_handle == "lo" else self._hi_var.get()) + amount
        )
        self.event_generate("<<Commit>>", data={
            "lovalue": self._lo_var.get(),
            "hivalue": self._hi_var.get(),
        })

    def _set_focused(self, value: float) -> None:
        value = max(self._minvalue, min(self._maxvalue, value))
        if self._focus_handle == "lo":
            self._lo_var.set(min(value, self._hi_var.get()))
        else:
            self._hi_var.set(max(value, self._lo_var.get()))

    def _cycle_handle(self, event: tk.Event) -> str:
        self._focus_handle = "hi" if self._focus_handle == "lo" else "lo"
        return "break"

    def _on_lo_write(self, *_: Any) -> None:
        self._sync()
        lo = self._lo_var.get()
        hi = self._hi_var.get()
        self.event_generate("<<Change>>", data={
            "lovalue": lo,
            "hivalue": hi,
            "prev_lovalue": self._prev_lovalue,
            "prev_hivalue": self._prev_hivalue,
        })
        self._prev_lovalue = lo
        self._prev_hivalue = hi

    def _on_hi_write(self, *_: Any) -> None:
        self._sync()
        lo = self._lo_var.get()
        hi = self._hi_var.get()
        self.event_generate("<<Change>>", data={
            "lovalue": lo,
            "hivalue": hi,
            "prev_lovalue": self._prev_lovalue,
            "prev_hivalue": self._prev_hivalue,
        })
        self._prev_lovalue = lo
        self._prev_hivalue = hi

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
        self._render_handles(colors)
        self._update_badge_colors(colors)
        self._setup_ticks()
        self._sync()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def lo_signal(self) -> Signal[float]:
        """Reactive Signal linked to the low-handle value."""
        return self._lo_signal

    @property
    def hi_signal(self) -> Signal[float]:
        """Reactive Signal linked to the high-handle value."""
        return self._hi_signal

    @property
    def lo_variable(self) -> tk.DoubleVar:
        """Underlying Tkinter DoubleVar for the low handle.

        See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
        """
        return self._lo_var

    @property
    def hi_variable(self) -> tk.DoubleVar:
        """Underlying Tkinter DoubleVar for the high handle.

        See [tkinter Variables](https://docs.python.org/3/library/tkinter.html#tkinter-variables).
        """
        return self._hi_var

    @property
    def lovalue(self) -> float:
        """Current low-handle value."""
        return self._lo_var.get()

    @property
    def hivalue(self) -> float:
        """Current high-handle value."""
        return self._hi_var.get()

    def get_lo(self) -> float:
        """Return the current low-handle value."""
        return self._lo_var.get()

    def get_hi(self) -> float:
        """Return the current high-handle value."""
        return self._hi_var.get()

    def set_lo(self, value: float) -> None:
        """Set the low handle to a new value, clamped to [minvalue, hivalue].

        Args:
            value: New low-handle value.
        """
        self._lo_var.set(max(self._minvalue, min(float(value), self._hi_var.get())))

    def set_hi(self, value: float) -> None:
        """Set the high handle to a new value, clamped to [lovalue, maxvalue].

        Args:
            value: New high-handle value.
        """
        self._hi_var.set(min(self._maxvalue, max(float(value), self._lo_var.get())))

    def on_changed(self, callback: Callable[[RangeSliderEventData], None]) -> str:
        """Register a callback for ``<<Change>>`` events.

        Args:
            callback: Called with a Tkinter event; ``event.data["lovalue"]``
                and ``event.data["hivalue"]`` are the current handle values;
                ``event.data["prev_lovalue"]`` and ``event.data["prev_hivalue"]``
                are the values before the change.

        Returns:
            Bind ID — pass to `off_changed()` to unsubscribe.
        """
        return self.bind("<<Change>>", callback, add="+")

    def off_changed(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<Change>>``.

        Args:
            bind_id: ID returned by `on_changed()`. If None, removes all.
        """
        self.unbind("<<Change>>", bind_id)

    def on_commit(self, callback: Callable[[RangeSliderCommitEventData], None]) -> str:
        """Register a callback for ``<<Commit>>`` events.

        Fires on mouse release and keyboard commit. Use for expensive
        downstream operations.

        Args:
            callback: Called with a Tkinter event; ``event.data["lovalue"]``
                and ``event.data["hivalue"]`` are the committed values.

        Returns:
            Bind ID — pass to `off_commit()` to unsubscribe.
        """
        return self.bind("<<Commit>>", callback, add="+")

    def off_commit(self, bind_id: str | None = None) -> None:
        """Unsubscribe from ``<<Commit>>``.

        Args:
            bind_id: ID returned by `on_commit()`. If None, removes all.
        """
        self.unbind("<<Commit>>", bind_id)

    # ------------------------------------------------------------------
    # Configure delegates
    # ------------------------------------------------------------------

    @configure_delegate('lovalue')
    def _delegate_lovalue(self, value=None):
        if value is None:
            return self._lo_var.get()
        self.set_lo(value)

    @configure_delegate('hivalue')
    def _delegate_hivalue(self, value=None):
        if value is None:
            return self._hi_var.get()
        self.set_hi(value)

    @configure_delegate('minvalue')
    def _delegate_minvalue(self, value=None):
        if value is None:
            return self._minvalue
        self._minvalue = float(value)
        self._setup_ticks()
        self._sync()

    @configure_delegate('maxvalue')
    def _delegate_maxvalue(self, value=None):
        if value is None:
            return self._maxvalue
        self._maxvalue = float(value)
        self._setup_ticks()
        self._sync()

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
        self._render_handles(self._colors)
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
