import bootstack as bs


def hero():
    with bs.App(title="Gauge", padding=20, gap=8) as app:
        with bs.Row(gap=20):
            bs.Gauge(value=68, variant="full", subtitle="Full")
            bs.Gauge(value=68, variant="semi", subtitle="Semi")
    app.run()


def accents():
    with bs.App(title="Gauge — Accents", padding=20) as app:
        with bs.Row(gap=12):
            for accent in ("primary", "secondary", "info", "success", "warning", "danger"):
                bs.Gauge(value=65, accent=accent, size=140, thickness=14, subtitle=accent.title())
    app.run()


def segments():
    with bs.App(title="Gauge — Segments", padding=20) as app:
        with bs.Row(gap=20):
            bs.Gauge(value=55, subtitle="Solid",         accent="primary")
            bs.Gauge(value=55, segment_width=8,  subtitle="Segmented",    accent="primary")
            bs.Gauge(value=55, segment_width=4,  subtitle="Fine segments", accent="secondary")
    app.run()


def thickness():
    with bs.App(title="Gauge — Thickness", padding=20) as app:
        with bs.Row(gap=20):
            bs.Gauge(value=70, thickness=6,  subtitle="Thin",    accent="info")
            bs.Gauge(value=70, thickness=14, subtitle="Default", accent="info")
            bs.Gauge(value=70, thickness=24, subtitle="Thick",   accent="info")
    app.run()


SCENES = {
    "hero":      hero,
    "accents":   accents,
    "segments":  segments,
    "thickness": thickness,
}