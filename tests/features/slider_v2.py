"""Visual test for bs.Slider and bs.RangeSlider — v2 comprehensive feature coverage.

Covers: accent variants, show_value, tick marks, tick_format, show_minmax,
disabled state, vertical orientation, RangeSlider, Signal binding,
on_changed with prev_value.

Run: python tests/features/slider_v2.py
"""
import bootstack as bs


class SliderDemo(bs.App):
    def __init__(self):
        super().__init__(title="Slider v2", size=(720, 960))
        self._build()

    def _build(self):
        root = bs.ScrollView(self)
        root.pack(fill="both", expand=True)
        c = root.add(padding=24)

        bs.Label(c, text="Slider & RangeSlider — v2", font="heading-lg[bold]").pack(
            anchor="w", pady=(0, 4))
        bs.Label(c, text="Horizontal, vertical, signal, and event features.", font="body").pack(
            anchor="w", pady=(0, 20))

        # ── Accent variants ─────────────────────────────────────────────────
        card1 = bs.Card(c)
        card1.pack(fill="x", pady=(0, 12))
        bs.Label(card1, text="Accent variants", font="body[bold]").pack(anchor="w", pady=(0, 10))
        for accent in ("primary", "success", "warning", "danger"):
            row = bs.PackFrame(card1, direction="row", gap=12, fill_items="none")
            row.pack(fill="x", pady=2)
            bs.Label(row, text=accent, width=9, anchor="e", font="body").pack()
            bs.Slider(row, accent=accent, value=50).pack(fill="x", expand=True)

        # ── Feature showcase ────────────────────────────────────────────────
        card2 = bs.Card(c)
        card2.pack(fill="x", pady=(0, 12))
        bs.Label(card2, text="Features — horizontal", font="body[bold]").pack(anchor="w", pady=(0, 10))

        bs.Label(card2, text="show_value=True, tick_format='{:.1f}'", font="body").pack(
            anchor="w", pady=(0, 2))
        self._s_badge = bs.Slider(card2, value=42, show_value=True, tick_format="{:.1f}")
        self._s_badge.pack(fill="x", pady=(0, 12))

        bs.Label(card2, text="tick_interval=25, minor_ticks=4, show_value, accent='success'",
                 font="body").pack(anchor="w", pady=(0, 2))
        self._s_tick = bs.Slider(
            card2, value=50, tick_interval=25, minor_ticks=4,
            show_value=True, accent="success",
        )
        self._s_tick.pack(fill="x", pady=(0, 12))

        bs.Label(card2, text="show_minmax=True, tick_format='${:.0f}', accent='warning'",
                 font="body").pack(anchor="w", pady=(0, 2))
        bs.Slider(
            card2, value=250, minvalue=0, maxvalue=500,
            show_minmax=True, tick_format="${:.0f}", accent="warning",
        ).pack(fill="x", pady=(0, 12))

        bs.Label(card2, text="state='disabled'", font="body").pack(anchor="w", pady=(0, 2))
        bs.Slider(card2, value=60, state="disabled").pack(fill="x")

        # ── RangeSlider horizontal ──────────────────────────────────────────
        card3 = bs.Card(c)
        card3.pack(fill="x", pady=(0, 12))
        bs.Label(card3, text="RangeSlider — horizontal", font="body[bold]").pack(
            anchor="w", pady=(0, 10))

        bs.Label(card3, text="show_value=True", font="body").pack(anchor="w", pady=(0, 2))
        self._range1 = bs.RangeSlider(card3, lovalue=20, hivalue=70, show_value=True)
        self._range1.pack(fill="x", pady=(0, 12))

        bs.Label(card3, text="tick_interval=25, minor_ticks=1, show_value, accent='success'",
                 font="body").pack(anchor="w", pady=(0, 2))
        self._range2 = bs.RangeSlider(
            card3, lovalue=25, hivalue=75,
            tick_interval=25, minor_ticks=1,
            show_value=True, accent="success",
        )
        self._range2.pack(fill="x", pady=(0, 12))

        bs.Label(card3, text="state='disabled', accent='danger'", font="body").pack(
            anchor="w", pady=(0, 2))
        bs.RangeSlider(card3, lovalue=30, hivalue=70, state="disabled", accent="danger").pack(
            fill="x")

        # ── Vertical orientation ────────────────────────────────────────────
        card4 = bs.Card(c)
        card4.pack(fill="x", pady=(0, 12))
        bs.Label(card4, text="Vertical orientation", font="body[bold]").pack(
            anchor="w", pady=(0, 10))

        vert_h = 200

        vert_row = bs.PackFrame(card4, direction="row", gap=28)
        vert_row.pack(anchor="w")

        def _add_vert(label: str, **kw):
            kw["orient"] = "vertical"
            col = bs.PackFrame(vert_row, direction="column", gap=4)
            col.pack()
            bs.Label(col, text=label, font="body", anchor="center").pack()
            s = bs.Slider(col, **kw)
            s.pack()
            s.configure(height=vert_h)

        _add_vert("primary",    accent="primary",  value=65)
        _add_vert("success",    accent="success",  value=40)
        _add_vert("warning",    accent="warning",  value=80)
        _add_vert("show_value", accent="primary",  value=55, show_value=True)
        _add_vert("ticks",      accent="danger",   value=75, tick_interval=25)
        _add_vert("disabled",   value=50,          state="disabled")

        # Vertical RangeSlider
        rs_col = bs.PackFrame(vert_row, direction="column", gap=4)
        rs_col.pack()
        bs.Label(rs_col, text="range", font="body", anchor="center").pack()
        self._range_v = bs.RangeSlider(
            rs_col, orient="vertical", lovalue=25, hivalue=75,
            show_value=True, accent="primary",
        )
        self._range_v.pack()
        self._range_v.configure(height=vert_h)

        # ── Signal & event ──────────────────────────────────────────────────
        card5 = bs.Card(c)
        card5.pack(fill="x", pady=(0, 12))
        bs.Label(card5, text="Signal & on_changed event", font="body[bold]").pack(
            anchor="w", pady=(0, 10))

        sig = bs.Signal(50.0)
        self._sig_slider = bs.Slider(
            card5, signal=sig, value=50,
            show_value=True, tick_interval=25, accent="primary",
        )
        self._sig_slider.pack(fill="x", pady=(0, 8))

        sig_lbl = bs.Label(card5, text="Signal.get() → 50.0", font="body")
        sig_lbl.pack(anchor="w", pady=(0, 2))

        event_lbl = bs.Label(card5, text="on_changed → value=50.0  prev=50.0", font="body")
        event_lbl.pack(anchor="w")

        sig.var.trace_add("write", lambda *_: sig_lbl.configure(
            text=f"Signal.get() → {sig.get():.1f}"))

        def _on_change(e):
            event_lbl.configure(
                text=(f"on_changed → value={e.data['value']:.1f}"
                      f"  prev={e.data['prev_value']:.1f}"))

        self._sig_slider.on_changed(_on_change)

        # ── Live value readout ──────────────────────────────────────────────
        self._readout = bs.Label(c, text="", font="body")
        self._readout.pack(anchor="w", pady=(8, 0))
        self._poll()

    def _poll(self):
        self._readout.configure(text=(
            f"badge={self._s_badge.value:.1f}  "
            f"tick={self._s_tick.value:.0f}  "
            f"h-range={self._range1.lovalue:.0f}–{self._range1.hivalue:.0f}  "
            f"h-range2={self._range2.lovalue:.0f}–{self._range2.hivalue:.0f}  "
            f"v-range={self._range_v.lovalue:.0f}–{self._range_v.hivalue:.0f}"
        ))
        self.after(100, self._poll)


if __name__ == "__main__":
    SliderDemo().mainloop()
