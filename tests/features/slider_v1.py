"""Visual test for bs.Slider and bs.RangeSlider — v1 feature coverage.

Run: python tests/features/slider_v1.py
"""
import bootstack as bs


class SliderDemo(bs.App):
    def __init__(self):
        super().__init__(title="Slider v1", size=(640, 660))
        self._build()

    def _build(self):
        root = bs.ScrollView(self)
        root.pack(fill="both", expand=True)
        c = root.add(padding=24)

        # ── Title ──────────────────────────────────────────────────────
        bs.Label(c, text="Slider & RangeSlider — v1", font="heading-lg[bold]").pack(
            anchor="w", pady=(0, 16))

        # ── Basic horizontal sliders ────────────────────────────────────
        bs.Label(c, text="Accent variants", font="body[bold]").pack(anchor="w", pady=(8, 4))
        for accent in ("primary", "success", "warning", "danger"):
            row = bs.PackFrame(c, direction="row", gap=12, fill_items="none")
            row.pack(fill="x", pady=2)
            bs.Label(row, text=accent, width=9, anchor="e").pack()
            s = bs.Slider(row, accent=accent, value=50)
            s.pack(fill="x", expand=True)

        # ── Density ────────────────────────────────────────────────────
        bs.Label(c, text="Density", font="body[bold]").pack(anchor="w", pady=(16, 4))
        for density in ("compact", "normal", "spacious"):
            row = bs.PackFrame(c, direction="row", gap=12, fill_items="none")
            row.pack(fill="x", pady=2)
            bs.Label(row, text=density, width=9, anchor="e").pack()
            s = bs.Slider(row, density=density, value=60)
            s.pack(fill="x", expand=True)

        # ── Value badge ─────────────────────────────────────────────────
        bs.Label(c, text="show_value=True", font="body[bold]").pack(anchor="w", pady=(16, 4))
        self._badge_slider = bs.Slider(c, value=40, show_value=True, tick_format="{:.1f}")
        self._badge_slider.pack(fill="x", pady=4)

        # ── Tick marks ──────────────────────────────────────────────────
        bs.Label(c, text="tick_interval=20, minor_ticks=3", font="body[bold]").pack(
            anchor="w", pady=(16, 4))
        self._tick_slider = bs.Slider(
            c, value=40, tick_interval=20, minor_ticks=3,
            show_value=True,
        )
        self._tick_slider.pack(fill="x", pady=4)

        # ── Handle styles ───────────────────────────────────────────────
        bs.Label(c, text="Handle styles", font="body[bold]").pack(anchor="w", pady=(16, 4))
        for style in ("pill", "square"):
            row = bs.PackFrame(c, direction="row", gap=12, fill_items="none")
            row.pack(fill="x", pady=2)
            bs.Label(row, text=style, width=9, anchor="e").pack()
            s = bs.Slider(row, handle_style=style, value=50)
            s.pack(fill="x", expand=True)

        # ── Icon handle ─────────────────────────────────────────────────
        bs.Label(c, text="handle_icon='thermometer-half'", font="body[bold]").pack(
            anchor="w", pady=(16, 4))
        self._icon_slider = bs.Slider(
            c, value=65, handle_icon="thermometer-half",
            density="spacious", accent="danger",
        )
        self._icon_slider.pack(fill="x", pady=4)

        # ── RangeSlider ─────────────────────────────────────────────────
        bs.Label(c, text="RangeSlider — pill handles", font="body[bold]").pack(
            anchor="w", pady=(16, 4))
        self._range = bs.RangeSlider(c, lovalue=20, hivalue=70, show_value=True)
        self._range.pack(fill="x", pady=4)

        bs.Label(c, text="RangeSlider — square handles (joined capsule)",
                 font="body[bold]").pack(anchor="w", pady=(12, 4))
        self._range2 = bs.RangeSlider(
            c, lovalue=30, hivalue=80, handle_style="square",
            accent="success",
        )
        self._range2.pack(fill="x", pady=4)

        bs.Label(c, text="RangeSlider — ticks + icon handles",
                 font="body[bold]").pack(anchor="w", pady=(12, 4))
        self._range3 = bs.RangeSlider(
            c, lovalue=10, hivalue=90, tick_interval=25, minor_ticks=1,
            handle_icon="arrows-expand", accent="warning", density="spacious",
        )
        self._range3.pack(fill="x", pady=4)

        # ── Readout ─────────────────────────────────────────────────────
        self._readout = bs.Label(c, text="", font="body")
        self._readout.pack(anchor="w", pady=(16, 0))
        self._poll()

    def _poll(self):
        self._readout.configure(
            text=(
                f"badge: {self._badge_slider.value:.1f}  "
                f"tick: {self._tick_slider.value:.0f}  "
                f"icon: {self._icon_slider.value:.0f}  "
                f"range: {self._range.lovalue:.0f}–{self._range.hivalue:.0f}  "
                f"range2: {self._range2.lovalue:.0f}–{self._range2.hivalue:.0f}"
            )
        )
        self.after(100, self._poll)


if __name__ == "__main__":
    SliderDemo().mainloop()