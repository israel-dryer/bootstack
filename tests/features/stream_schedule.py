"""Visual test for Stream and Schedule APIs."""
import bootstack as bs
from bootstack.signals import Signal


def main():
    with bs.App(title="Stream + Schedule — visual test", minsize=(600, 500), padding=0) as app:
        with bs.ScrollView(fill="both", expand=True):
            with bs.VStack(padding=24, gap=20, fill_items="x", expand_items=True):

                log = Signal("(waiting...)")

                def emit(msg: str) -> None:
                    log.set(msg)

                # ----- Schedule -----
                bs.Label("Schedule — widget.schedule", font="heading-lg")

                with bs.GroupBox("after / idle / interval", fill="x", gap=6):
                    counter = Signal(0)
                    job_ref: list = [None]
                    sched = bs.Schedule(app.tk)

                    def _tick():
                        counter.set(counter.get() + 1)

                    with bs.HStack(gap=8, anchor_items="center"):
                        bs.Label("Tick count:")
                        bs.Label(text_signal=counter, color="#0d6efd")

                    def _start():
                        if job_ref[0] is None or not job_ref[0]:
                            job_ref[0] = sched.every(500, _tick)
                            emit("interval started (every 500ms)")

                    def _stop():
                        if job_ref[0]:
                            job_ref[0].cancel()
                            emit("interval cancelled")

                    def _once():
                        sched.delay(1000, lambda: emit("delay(1000) fired!"))
                        emit("after(1000) scheduled...")

                    with bs.HStack(gap=8):
                        bs.Button("Start interval", variant="outline", on_click=_start)
                        bs.Button("Stop", variant="outline", on_click=_stop)
                        bs.Button("After 1s", variant="outline", on_click=_once)

                # ----- Stream — basic -----
                bs.Label("Stream — on() without handler", font="heading-lg")

                with bs.GroupBox("on('change') → Stream → listen()", fill="x"):
                    tf_basic = bs.TextField(placeholder="type here...", fill="x")
                    sub_ref: list = [None]

                    def _attach():
                        if sub_ref[0]:
                            sub_ref[0].cancel()
                        sub_ref[0] = tf_basic.on("change").listen(
                            lambda e: emit(f"stream change: {tf_basic.value!r}")
                        )
                        emit("stream attached")

                    def _detach():
                        if sub_ref[0]:
                            sub_ref[0].cancel()
                            sub_ref[0] = None
                            emit("stream detached")

                    with bs.HStack(gap=8):
                        bs.Button("Attach stream", variant="outline", on_click=_attach)
                        bs.Button("Detach", variant="outline", on_click=_detach)

                # ----- Stream — debounce -----
                bs.Label("Stream — debounce(500)", font="heading-lg")

                with bs.GroupBox("Fires 500ms after you stop typing", fill="x"):
                    tf_debounce = bs.TextField(placeholder="type quickly...", fill="x")
                    tf_debounce.on("change").debounce(500).listen(
                        lambda e: emit(f"debounced: {tf_debounce.value!r}")
                    )

                # ----- Stream — filter + map -----
                bs.Label("Stream — filter + map", font="heading-lg")

                with bs.GroupBox("Only emits when length > 3, maps to uppercase", fill="x"):
                    tf_filter = bs.TextField(placeholder="type 4+ chars...", fill="x")
                    tf_filter.on("change").filter(
                        lambda e: len(tf_filter.value or "") > 3
                    ).map(
                        lambda e: type("E", (), {"data": (tf_filter.value or "").upper()})()
                    ).listen(
                        lambda e: emit(f"filtered+mapped: {e.data!r}")
                    )

                # ----- Stream — throttle -----
                bs.Label("Stream — throttle(1000)", font="heading-lg")

                with bs.GroupBox("Slider emits at most once per second", fill="x"):
                    sl = bs.Slider(50, show_value=True, fill="x")
                    sl.on("change").throttle(1000).listen(
                        lambda e: emit(f"throttled slider: {sl.value:.0f}")
                    )

                # ----- on_change shorthand (existing pattern unchanged) -----
                bs.Label("on_change(handler) — existing pattern unchanged", font="heading-lg")

                with bs.GroupBox("Direct callback, returns Subscription", fill="x"):
                    tf_direct = bs.TextField(placeholder="direct binding...", fill="x")
                    direct_sub = tf_direct.on_change(
                        lambda e: emit(f"direct on_change: {tf_direct.value!r}")
                    )
                    bs.Label(f"Subscription type: {type(direct_sub).__name__}", accent="secondary")

                # ----- on_change() → Stream (new pattern) -----
                bs.Label("on_change() — returns Stream", font="heading-lg")

                with bs.GroupBox("No handler → Stream → debounce → listen", fill="x"):
                    tf_stream = bs.TextField(placeholder="stream shorthand...", fill="x")
                    tf_stream.on_change().debounce(400).listen(
                        lambda e: emit(f"on_change() stream: {tf_stream.value!r}")
                    )

                # ----- Status -----
                bs.Separator()
                with bs.HStack(gap=8, anchor_items="center"):
                    bs.Label("Log:", font="label[bold]")
                    bs.Label(text_signal=log, color="#0d6efd")

    app.run()


if __name__ == "__main__":
    main()
