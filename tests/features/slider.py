"""Visual test for public Slider and RangeSlider widgets."""
from bootstack import App, VStack, HStack, Label, Slider, RangeSlider, Button
from bootstack.signals import Signal


def main():
    with App(title="Slider + RangeSlider — visual test", minsize=(520, 100), padding=24, gap=16) as app:

        readout = Signal("(move a handle)")

        # Basic horizontal slider
        Label("Slider — basic")
        s1 = Slider(50, min_value=0, max_value=100, fill="x", expand=True)
        s1.on_change(lambda e: readout.set(f"slider: {s1.value:.0f}"))

        # With value badge and ticks
        Label("Slider — show_value + ticks")
        Slider(
            25, min_value=0, max_value=100,
            show_value=True,
            tick_step=25,
            fill="x", expand=True,
        )

        # With min/max labels
        Label("Slider — show_minmax")
        Slider(
            60, min_value=0, max_value=200,
            show_minmax=True,
            tick_format="{:.0f}°",
            fill="x", expand=True,
        )

        # Signal-driven
        Label("Slider — signal-driven")
        sig = Signal(40.0)
        with HStack(gap=12, anchor_items="center", fill="x", expand=True):
            Slider(signal=sig, fill="x", expand=True)
            Button("→ 80", on_click=lambda: sig.set(80.0), variant="outline")

        # RangeSlider
        Label("RangeSlider — basic")
        r1 = RangeSlider(20, 75, min_value=0, max_value=100, fill="x", expand=True)
        r1.on_change(lambda e: readout.set(f"range: {r1.low_value:.0f} – {r1.high_value:.0f}"))

        # RangeSlider with value badges and ticks
        Label("RangeSlider — show_value + ticks")
        RangeSlider(
            10, 90, min_value=0, max_value=100,
            show_value=True,
            tick_step=10,
            fill="x", expand=True,
        )

        # Readout
        with HStack(gap=8, anchor_items="center"):
            Label("Last change:")
            Label(text_signal=readout, color="#0d6efd")

    app.run()


if __name__ == "__main__":
    main()
