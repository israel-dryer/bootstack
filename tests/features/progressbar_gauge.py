"""Visual test for public ProgressBar and Gauge widgets."""
from bootstack import (
    App, VStack, HStack, Grid, Label, ProgressBar, Gauge, Button
)


with App(title="ProgressBar + Gauge — visual test", minsize=(560, 100), padding=24, gap=16) as app:

    pb = ProgressBar(0, max_value=100, accent="primary", fill="x", expand=True)

    # ProgressBar variants
    Label("ProgressBar — accents")
    for accent in ("primary", "success", "warning", "danger"):
        ProgressBar(40, accent=accent, fill="x", expand=True)

    Label("ProgressBar — thin variant")
    ProgressBar(60, accent="primary", variant="thin", fill="x", expand=True)

    Label("ProgressBar — controlled")
    with HStack(gap=8, anchor_items="center"):
        pb
        Button("+10", on_click=lambda: pb.step(10), variant="outline")
        Button("Reset", on_click=lambda: setattr(pb, "value", 0), variant="outline")

    Label("ProgressBar — indeterminate")
    pb_ind = ProgressBar(mode="indeterminate", accent="success", fill="x", expand=True)
    with HStack(gap=8):
        Button("Start", on_click=lambda: pb_ind.start(), variant="outline")
        Button("Stop", on_click=lambda: pb_ind.stop(), variant="outline")

    # Gauge variants
    Label("Gauge")
    with HStack(gap=24):
        Gauge(72, subtitle="CPU", value_suffix="%", accent="primary", size=150)
        Gauge(45, subtitle="Memory", value_suffix="%", accent="warning", size=150)
        Gauge(18, subtitle="Disk", value_suffix="%", accent="success", size=150)

    Label("Gauge — semi-circle")
    with HStack(gap=24):
        Gauge(60, meter_type="semi", value_suffix="°C", subtitle="Temp",
              accent="danger", size=150, thickness=14)
        Gauge(33, meter_type="semi", value_suffix="%", subtitle="Load",
              size=150, thickness=14)

app.run()
