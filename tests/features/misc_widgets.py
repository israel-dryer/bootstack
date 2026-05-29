"""Visual test for ScrollView, SpinnerField, TimeField, and MenuBar."""
from bootstack import (
    App, VStack, HStack, Label, Button,
    MenuBar, ScrollView, SpinnerField, TimeField,
)
from bootstack.signals import Signal


def main():
    with App(title="Misc Widgets — visual test", size=(680, 600), padding=0, gap=0) as app:

        # --- MenuBar ---
        mb = MenuBar(fill="x")
        mb.add_button("File", region="before", on_click=lambda: print("File"))
        mb.add_button("Edit", region="before", on_click=lambda: print("Edit"))
        mb.add_label("bootstack demo", region="center")
        mb.add_button("Help", region="after", on_click=lambda: print("Help"))

        # --- Body ---
        with VStack(padding=16, gap=16, fill="both", expand=True):

            # SpinnerField — text mode
            Label("SpinnerField — text mode (options=)")
            spin_text = SpinnerField(
                options=["Small", "Medium", "Large", "X-Large"],
                value="Medium",
                label="T-Shirt Size",
                wrap=True,
            )

            # SpinnerField — numeric mode
            Label("SpinnerField — numeric mode")
            spin_num = SpinnerField(
                value=5,
                min_value=0,
                max_value=20,
                step=1,
                label="Quantity",
                wrap=False,
            )

            # TimeField
            Label("TimeField")
            with HStack(gap=8):
                tf = TimeField(label="Meeting time", interval=30)
                TimeField(label="End time", value_format="HH:mm", interval=15, disabled=True)

            # Readout
            status = Signal("(interact with fields above)")
            Label(textsignal=status)

            spin_text.on_change(lambda e: status.set(f"size: {spin_text.value}"))
            spin_num.on_change(lambda e: status.set(f"qty: {spin_num.value}"))
            tf.on_change(lambda e: status.set(f"time: {tf.value}"))

            # ScrollView
            Label("ScrollView (10 rows, fixed height)")
            with ScrollView(scroll_direction="vertical", fill="x") as sv:
                for i in range(10):
                    with HStack(gap=8, padding=4, fill="x"):
                        Label(f"Row {i + 1}", width=8)
                        Button(f"Action {i + 1}", on_click=lambda i=i: status.set(f"clicked row {i + 1}"))

    app.run()


if __name__ == "__main__":
    main()
