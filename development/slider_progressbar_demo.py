"""
Feasibility demo: Canvas track + overlay handle(s) → modern slider widgets.

Covers single Slider and two-handle RangeSlider, both with keyboard support.

Run: python development/slider_progressbar_demo.py
"""
import tkinter as tk
from tkinter import ttk

try:
    from PIL import Image, ImageDraw, ImageTk
    _PIL = True
except ImportError:
    _PIL = False


def _make_handle(size: int, fill: str, border: str, border_px: int = 3):
    if not _PIL:
        return None
    s = size * 2
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, s - 1, s - 1], fill=border)
    p = border_px * 2
    d.ellipse([p, p, s - 1 - p, s - 1 - p], fill=fill)
    return ImageTk.PhotoImage(img.resize((size, size), Image.LANCZOS))


class _Slider(tk.Frame):
    TRACK_H = 6
    TROUGH_COLOR = "#dee2e6"
    STEP = 1
    STEP_LARGE = 10

    def __init__(self, master, maximum=100, value=0, handle_img=None,
                 accent="#0d6efd", **kw):
        handle_size = handle_img.width() if handle_img else 18
        bg = kw.get("bg", master.cget("bg"))
        super().__init__(master, height=handle_size,
                         takefocus=True,
                         highlightthickness=2,
                         highlightcolor=accent,
                         highlightbackground=bg,
                         **kw)
        self.pack_propagate(False)

        self._max = maximum
        self._half = handle_size // 2
        self._var = tk.DoubleVar(value=value)
        self._handle_img = handle_img

        self._canvas = tk.Canvas(self, height=self.TRACK_H, bg=bg, highlightthickness=0)
        self._canvas.place(x=self._half, rely=0.5, anchor="w",
                           height=self.TRACK_H, width=100)
        self._trough = self._canvas.create_rectangle(
            0, 0, 100, self.TRACK_H, fill=self.TROUGH_COLOR, outline="")
        self._fill = self._canvas.create_rectangle(
            0, 0, 0, self.TRACK_H, fill=accent, outline="")

        if handle_img:
            self._handle = tk.Label(self, image=handle_img, bd=0, bg=bg, cursor="hand2")
        else:
            self._handle = tk.Frame(
                self, width=handle_size, height=handle_size, bg=accent, cursor="hand2")
        self._handle.place(x=0, rely=0.5, anchor="center")

        for w in (self._canvas, self._handle):
            w.bind("<Button-1>", self._on_click)
            w.bind("<B1-Motion>", self._on_drag)

        self.bind("<Left>",       lambda e: self._step(-self.STEP))
        self.bind("<Right>",      lambda e: self._step(+self.STEP))
        self.bind("<Down>",       lambda e: self._step(-self.STEP))
        self.bind("<Up>",         lambda e: self._step(+self.STEP))
        self.bind("<Shift-Left>",  lambda e: self._step(-self.STEP_LARGE))
        self.bind("<Shift-Right>", lambda e: self._step(+self.STEP_LARGE))
        self.bind("<Home>",       lambda e: self._var.set(0))
        self.bind("<End>",        lambda e: self._var.set(self._max))

        # Clicking track/handle focuses the frame for keyboard input
        for w in (self._canvas, self._handle):
            w.bind("<Button-1>", self._focus_and_click, add=True)

        self._var.trace_add("write", self._sync)
        self.bind("<Configure>", self._on_configure)

    def _focus_and_click(self, _event: tk.Event):
        self.focus_set()

    def _on_configure(self, event: tk.Event):
        w = event.width
        if w > self._half * 2:
            track_w = w - self._half * 2
            self._canvas.place_configure(width=track_w)
            self._canvas.coords(self._trough, 0, 0, track_w, self.TRACK_H)
            self._sync()

    def _track_range(self):
        return self._half, self.winfo_width() - self._half

    def _on_click(self, event: tk.Event):
        x = event.widget.winfo_x() + event.x
        start, end = self._track_range()
        ratio = (x - start) / max(1, end - start)
        self._var.set(max(0.0, min(float(self._max), ratio * self._max)))

    def _on_drag(self, event: tk.Event):
        self._on_click(event)

    def _step(self, amount: float):
        self._var.set(max(0.0, min(float(self._max), self._var.get() + amount)))

    def _sync(self, *_):
        start, end = self._track_range()
        ratio = self._var.get() / self._max
        track_w = end - start
        self._canvas.coords(self._fill, 0, 0, int(ratio * track_w), self.TRACK_H)
        self._handle.place_configure(x=start + int(ratio * track_w))

    @property
    def value(self) -> float:
        return self._var.get()


class _RangeSlider(tk.Frame):
    TRACK_H = 6
    TROUGH_COLOR = "#dee2e6"
    STEP = 1
    STEP_LARGE = 10

    def __init__(self, master, maximum=100, lo=25, hi=75, handle_img=None,
                 accent="#0d6efd", **kw):
        handle_size = handle_img.width() if handle_img else 18
        bg = kw.get("bg", master.cget("bg"))
        super().__init__(master, height=handle_size,
                         takefocus=True,
                         highlightthickness=2,
                         highlightcolor=accent,
                         highlightbackground=bg,
                         **kw)
        self.pack_propagate(False)

        self._max = maximum
        self._half = handle_size // 2
        self._lo = tk.DoubleVar(value=lo)
        self._hi = tk.DoubleVar(value=hi)
        self._handle_img = handle_img
        self._dragging = None
        self._focus_handle = "lo"  # which handle receives keyboard input

        self._canvas = tk.Canvas(self, height=self.TRACK_H, bg=bg, highlightthickness=0)
        self._canvas.place(x=self._half, rely=0.5, anchor="w",
                           height=self.TRACK_H, width=100)
        self._trough = self._canvas.create_rectangle(
            0, 0, 100, self.TRACK_H, fill=self.TROUGH_COLOR, outline="")
        self._fill = self._canvas.create_rectangle(
            0, 0, 0, self.TRACK_H, fill=accent, outline="")

        if handle_img:
            self._handle_lo = tk.Label(self, image=handle_img, bd=0, bg=bg, cursor="hand2")
            self._handle_hi = tk.Label(self, image=handle_img, bd=0, bg=bg, cursor="hand2")
        else:
            self._handle_lo = tk.Frame(
                self, width=handle_size, height=handle_size, bg=accent, cursor="hand2")
            self._handle_hi = tk.Frame(
                self, width=handle_size, height=handle_size, bg=accent, cursor="hand2")

        self._handle_lo.place(x=0, rely=0.5, anchor="center")
        self._handle_hi.place(x=0, rely=0.5, anchor="center")

        self._canvas.bind("<Button-1>", self._canvas_press)
        self._canvas.bind("<B1-Motion>", self._canvas_drag)
        self._canvas.bind("<Button-1>", self.focus_set, add=True)
        self._handle_lo.bind("<Button-1>", lambda e: self._handle_press(e, "lo"))
        self._handle_lo.bind("<B1-Motion>", self._handle_drag)
        self._handle_hi.bind("<Button-1>", lambda e: self._handle_press(e, "hi"))
        self._handle_hi.bind("<B1-Motion>", self._handle_drag)

        self.bind("<Left>",        lambda e: self._step(-self.STEP))
        self.bind("<Right>",       lambda e: self._step(+self.STEP))
        self.bind("<Down>",        lambda e: self._step(-self.STEP))
        self.bind("<Up>",          lambda e: self._step(+self.STEP))
        self.bind("<Shift-Left>",  lambda e: self._step(-self.STEP_LARGE))
        self.bind("<Shift-Right>", lambda e: self._step(+self.STEP_LARGE))
        self.bind("<Home>",        lambda e: self._set_focused(0))
        self.bind("<End>",         lambda e: self._set_focused(self._max))
        self.bind("<Tab>",         self._cycle_handle)

        self._lo.trace_add("write", self._sync)
        self._hi.trace_add("write", self._sync)
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event: tk.Event):
        w = event.width
        if w > self._half * 2:
            track_w = w - self._half * 2
            self._canvas.place_configure(width=track_w)
            self._canvas.coords(self._trough, 0, 0, track_w, self.TRACK_H)
            self._sync()

    def _track_range(self):
        return self._half, self.winfo_width() - self._half

    def _x_to_value(self, x: int) -> float:
        start, end = self._track_range()
        ratio = (x - start) / max(1, end - start)
        return max(0.0, min(float(self._max), ratio * self._max))

    def _value_to_x(self, value: float) -> int:
        start, end = self._track_range()
        return start + int((value / self._max) * (end - start))

    def _canvas_press(self, event: tk.Event):
        x = self._canvas.winfo_x() + event.x
        lo_x = self._value_to_x(self._lo.get())
        hi_x = self._value_to_x(self._hi.get())
        self._dragging = "lo" if abs(x - lo_x) <= abs(x - hi_x) else "hi"
        self._focus_handle = self._dragging
        self._move(x)

    def _canvas_drag(self, event: tk.Event):
        self._move(self._canvas.winfo_x() + event.x)

    def _handle_press(self, event: tk.Event, which: str):
        self._dragging = which
        self._focus_handle = which
        self.focus_set()

    def _handle_drag(self, event: tk.Event):
        self._move(event.widget.winfo_x() + event.x)

    def _move(self, x: int):
        value = self._x_to_value(x)
        if self._dragging == "lo":
            self._lo.set(min(value, self._hi.get()))
        else:
            self._hi.set(max(value, self._lo.get()))

    def _step(self, amount: float):
        self._set_focused(
            (self._lo.get() if self._focus_handle == "lo" else self._hi.get()) + amount
        )

    def _set_focused(self, value: float):
        value = max(0.0, min(float(self._max), value))
        if self._focus_handle == "lo":
            self._lo.set(min(value, self._hi.get()))
        else:
            self._hi.set(max(value, self._lo.get()))

    def _cycle_handle(self, event: tk.Event):
        self._focus_handle = "hi" if self._focus_handle == "lo" else "lo"
        return "break"  # prevent Tab from moving focus out of the widget

    def _sync(self, *_):
        start, end = self._track_range()
        track_w = end - start
        lo_x = int((self._lo.get() / self._max) * track_w)
        hi_x = int((self._hi.get() / self._max) * track_w)
        self._canvas.coords(self._fill, lo_x, 0, hi_x, self.TRACK_H)
        self._handle_lo.place_configure(x=start + lo_x)
        self._handle_hi.place_configure(x=start + hi_x)

    @property
    def lo(self) -> float:
        return self._lo.get()

    @property
    def hi(self) -> float:
        return self._hi.get()


class Demo(tk.Tk):
    BG = "#f8f9fa"
    ACCENT = "#0d6efd"

    def __init__(self):
        super().__init__()
        self.title("Slider Feasibility Demo")
        self.geometry("520x400")
        self.resizable(False, False)
        self.configure(bg=self.BG)

        ttk.Style(self).theme_use("clam")

        outer = tk.Frame(self, bg=self.BG, padx=50, pady=40)
        outer.pack(fill="both", expand=True)

        handle = _make_handle(22, self.ACCENT, "#ffffff")

        self._sliders = []
        for label, initial in [("Volume", 65), ("Brightness", 30)]:
            tk.Label(outer, text=label, bg=self.BG, font=("TkDefaultFont", 11)).pack(anchor="w")
            s = _Slider(outer, maximum=100, value=initial, handle_img=handle,
                        accent=self.ACCENT, bg=self.BG)
            s.pack(fill="x", pady=(4, 16))
            self._sliders.append(s)

        tk.Label(outer, text="Price range", bg=self.BG, font=("TkDefaultFont", 11)).pack(anchor="w")
        self._range = _RangeSlider(outer, maximum=100, lo=20, hi=70,
                                   handle_img=handle, accent=self.ACCENT, bg=self.BG)
        self._range.pack(fill="x", pady=(4, 16))

        hint = "Arrow keys adjust · Shift+Arrow ×10 · Home/End · Tab cycles range handles"
        tk.Label(outer, text=hint, bg=self.BG, fg="#6c757d",
                 font=("TkDefaultFont", 9)).pack(anchor="w", pady=(0, 8))

        self._readout = tk.Label(outer, text="", bg=self.BG, font=("TkDefaultFont", 10))
        self._readout.pack(anchor="w")
        self.after(100, self._poll)

    def _poll(self):
        self._readout.config(
            text=f"Volume: {self._sliders[0].value:.0f}   "
                 f"Brightness: {self._sliders[1].value:.0f}   "
                 f"Price: {self._range.lo:.0f} – {self._range.hi:.0f}"
        )
        self.after(100, self._poll)


if __name__ == "__main__":
    Demo().mainloop()