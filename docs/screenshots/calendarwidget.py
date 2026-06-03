from datetime import date
import bootstack as bs


def hero():
    with bs.App(title="Calendar", padding=20) as app:
        with bs.HStack(fill="x"):
            bs.Calendar(value=date(2026, 5, 15))

    app.run()


def range_select():
    with bs.App(title="Calendar — Range", padding=20) as app:
        with bs.HStack(fill="x"):
            bs.Calendar(
                selection_mode="range",
                start_date=date(2026, 5, 20),
                end_date=date(2026, 6, 10),
            )

    app.run()


def week_numbers():
    with bs.App(title="Calendar — Week Numbers", padding=20) as app:
        with bs.HStack(fill="x"):
            bs.Calendar(value=date(2026, 5, 15), show_week_numbers=True)

    app.run()


SCENES = {
    "hero":         hero,
    "range":        range_select,
    "week-numbers": week_numbers,
}