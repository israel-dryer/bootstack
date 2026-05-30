"""Visual test for api gap fixes — insert_addon, new properties, and event shorthands."""
import bootstack as bs
from bootstack.signals import Signal


def main():
    with bs.App(title="API gap fixes — visual test", minsize=(640, 500), padding=0) as app:
        with bs.ScrollView(fill="both", expand=True):
            with bs.VStack(padding=24, gap=20, fill_items="x", expand_items=True):

                status = Signal("(no events yet)")

                def log(msg):
                    status.set(msg)

                # ----- insert_addon -----
                bs.Label("insert_addon — label before, button after")
                tf = bs.TextField(placeholder="search…", label="Search", fill="x", expand=True)
                tf.insert_addon("label", "before", icon="search")
                tf.insert_addon("button", "after", icon="x-lg", name="clear", command=tf.clear)

                bs.Label("insert_addon — toggle before")
                nf = bs.NumberField(label="Amount", fill="x", expand=True)
                nf.insert_addon("toggle", "before", text="$", signal=Signal(False))

                # ----- placeholder property -----
                bs.Label("TextField.placeholder property")
                tf_ph = bs.TextField(placeholder="e.g. Jane Smith", label="Read placeholder back")
                with bs.HStack(gap=8, anchor_items="center"):
                    bs.Label("placeholder =")
                    bs.Label(text_signal=Signal(tf_ph.placeholder or "(none)"), color="#0d6efd")

                # ----- NumberField.read_only property -----
                bs.Label("NumberField.read_only property")
                nf_ro = bs.NumberField(42, label="Read-only (togglable)")
                with bs.HStack(gap=8):
                    bs.Button(
                        "Toggle read-only",
                        on_click=lambda: setattr(nf_ro, "read_only", not nf_ro.read_only),
                        variant="outline",
                    )

                # ----- Slider min_value / max_value / disabled -----
                bs.Label("Slider — min_value / max_value / disabled")
                bs.Label("(disabled blocks user drag; 'Set 75' shows programmatic set still works)",
                         font="label", accent="secondary")
                sl = bs.Slider(50, show_value=True, fill="x", expand=True)
                with bs.HStack(gap=8):
                    bs.Button("range 0–100", variant="outline", on_click=lambda: [
                        setattr(sl, "min_value", 0), setattr(sl, "max_value", 100)])
                    bs.Button("range 0–200", variant="outline", on_click=lambda: [
                        setattr(sl, "min_value", 0), setattr(sl, "max_value", 200)])
                    bs.Button("Toggle disabled", variant="outline",
                              on_click=lambda: setattr(sl, "disabled", not sl.disabled))
                    bs.Button("Set 75", variant="outline",
                              on_click=lambda: setattr(sl, "value", 75))

                # ----- ProgressBar max_value -----
                bs.Label("ProgressBar — max_value property")
                pb = bs.ProgressBar(0, max_value=100, accent="primary", fill="x", expand=True)
                pb_status = Signal(f"value=0  max={pb.max_value:.0f}")

                def pb_step():
                    pb.step(10)
                    pb_status.set(f"value={pb.value:.0f}  max={pb.max_value:.0f}")

                def pb_set_max(v):
                    pb.max_value = v
                    pb_status.set(f"value={pb.value:.0f}  max={pb.max_value:.0f}")

                with bs.HStack(gap=8, anchor_items="center"):
                    bs.Label(text_signal=pb_status, color="#0d6efd")
                    bs.Button("+10 value", on_click=pb_step, variant="outline")
                    bs.Button("max=50", on_click=lambda: pb_set_max(50), variant="outline")
                    bs.Button("max=100", on_click=lambda: pb_set_max(100), variant="outline")

                # ----- Gauge on_change -----
                bs.Label("Gauge — on_change (interactive, drag to change)")
                gauge = bs.Gauge(40, interactive=True, size=160, subtitle="drag me",
                                 value_suffix="%", accent="primary")
                gauge.on_change(lambda e: log(f"gauge → {gauge.value}"))

                # ----- Validation events -----
                bs.Label("TextField — on_valid / on_invalid (required, press Enter to validate)")
                tf_val = bs.TextField(label="Required", required=True, fill="x", expand=True)
                tf_val.on_valid(lambda e: log("valid ✓"))
                tf_val.on_invalid(lambda e: log("invalid ✗"))

                bs.Label("NumberField — on_valid / on_invalid")
                nf_val = bs.NumberField(label="Min 10", min_value=10, fill="x", expand=True)
                nf_val.on_valid(lambda e: log("number valid ✓"))
                nf_val.on_invalid(lambda e: log("number invalid ✗"))

                # ----- Spinbox on_submit -----
                bs.Label("Spinbox — on_submit (press Enter)")
                sb = bs.Spinbox(options=["Alpha", "Beta", "Gamma"])
                sb.on_submit(lambda e: log(f"spinbox submitted → {sb.value!r}"))

                # ----- Status readout -----
                with bs.HStack(gap=8, anchor_items="center"):
                    bs.Label("Event log:")
                    bs.Label(text_signal=status, color="#0d6efd")

    app.run()


if __name__ == "__main__":
    main()
