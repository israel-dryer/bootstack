"""Visual test for public Spinbox and Separator widgets."""
from bootstack import App, VStack, HStack, Label, Spinbox, Separator


def main():
    with App(title="Spinbox + Separator — visual test", minsize=(400, 100), padding=24, gap=12) as app:

        # List-based
        Label("Spinbox — fixed options")
        Spinbox("Medium", options=["Small", "Medium", "Large", "X-Large"])

        Label("Spinbox — text list, wrap=True")
        Spinbox("Mon", options=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], wrap=True)

        Separator(fill="x")

        # Numeric range
        Label("Spinbox — numeric range")
        Spinbox(5, min_value=0, max_value=20, step=1)

        Label("Spinbox — float range, step=0.5")
        Spinbox(1.5, min_value=0.0, max_value=5.0, step=0.5)

        Separator(fill="x")

        # States
        Label("Spinbox — disabled")
        Spinbox("Medium", options=["Small", "Medium", "Large"], disabled=True)

        Label("Spinbox — compact density")
        Spinbox(3, min_value=1, max_value=10, density="compact")

        Separator(fill="x")

        # Separator orientations
        Label("Separator — horizontal (default)")
        Separator(fill="x")

        Label("Separator — accented")
        Separator(accent="primary", fill="x")

        Label("Separators — vertical, inside HStack")
        with HStack(gap=12, fill_items="y"):
            Label("Left")
            Separator("vertical")
            Label("Middle")
            Separator("vertical")
            Label("Right")

    app.run()


if __name__ == "__main__":
    main()
