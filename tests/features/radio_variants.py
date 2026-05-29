"""Visual test for public Radio and RadioToggleButton widgets."""
from bootstack import (
    App, VStack, HStack, Label, Separator,
    Radio, RadioToggleButton,
)
from bootstack.signals import Signal


def main():
    with App(title="Radio + RadioToggleButton", minsize=(520, 540), padding=20, gap=16) as app:

        # --- Radio ---
        Label("Radio — shared Signal group", font="heading-lg")

        with HStack(gap=12, fill="x"):
            with VStack(gap=6, fill="x", expand=True):
                Label("Default (pre-selected B)")
                sig_a = Signal("b")
                Radio("Option A", "a", signal=sig_a)
                Radio("Option B", "b", signal=sig_a)
                Radio("Option C", "c", signal=sig_a)

            with VStack(gap=6, fill="x", expand=True):
                Label("Success accent")
                sig_b = Signal("x")
                Radio("Choice X", "x", signal=sig_b, accent="success")
                Radio("Choice Y", "y", signal=sig_b, accent="success")
                Radio("Choice Z", "z", signal=sig_b, accent="success")

        with HStack(gap=12, fill="x"):
            with VStack(gap=6, fill="x", expand=True):
                Label("on_change callback")
                sig_c = Signal("one")
                cb_lbl = Label("selected: one")

                def _update(e):
                    cb_lbl.value = f"selected: {sig_c.get()}"

                r1 = Radio("One", "one", signal=sig_c)
                r2 = Radio("Two", "two", signal=sig_c)
                r3 = Radio("Three", "three", signal=sig_c)
                r1.on_change(_update)
                r2.on_change(_update)
                r3.on_change(_update)

            with VStack(gap=6, fill="x", expand=True):
                Label("Disabled option")
                sig_d = Signal("yes")
                Radio("Yes", "yes", signal=sig_d)
                Radio("No", "no", signal=sig_d)
                Radio("Unavailable", "na", signal=sig_d, disabled=True)

        Separator(fill="x")

        # --- RadioToggleButton ---
        Label("RadioToggleButton — toggle-button style", font="heading-lg")

        with VStack(gap=10, fill="x"):
            Label("Horizontal segmented control")
            sig_e = Signal("day")
            with HStack(gap=4):
                RadioToggleButton("Day", "day", signal=sig_e)
                RadioToggleButton("Week", "week", signal=sig_e)
                RadioToggleButton("Month", "month", signal=sig_e)
                RadioToggleButton("Year", "year", signal=sig_e)

            Label("Primary accent")
            sig_f = Signal("s")
            with HStack(gap=4):
                RadioToggleButton("S", "s", signal=sig_f, accent="primary")
                RadioToggleButton("M", "m", signal=sig_f, accent="primary")
                RadioToggleButton("L", "l", signal=sig_f, accent="primary")
                RadioToggleButton("XL", "xl", signal=sig_f, accent="primary")

            Label("Compact density")
            sig_g = Signal("left")
            with HStack(gap=4):
                RadioToggleButton("Left", "left", signal=sig_g, density="compact")
                RadioToggleButton("Center", "center", signal=sig_g, density="compact")
                RadioToggleButton("Right", "right", signal=sig_g, density="compact")

    app.run()


if __name__ == "__main__":
    main()