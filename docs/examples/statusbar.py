import bootstack as bs

with bs.App(title="StatusBar demo", minsize=(720, 360), padding=16) as app:

    with bs.Column(grow=True, horizontal_items="stretch", gap=16):

        # ── Text segments + clusters ───────────────────────────────────────
        with bs.Column(gap=4):
            bs.Label("Segments and clusters", font="heading-sm")
            sb1 = bs.StatusBar(horizontal="stretch")
            sb1.add_text("Ready", icon="check-circle")
            sb1.add_text("Ln 12, Col 5", side="right")
            sb1.add_text("UTF-8", side="right")
            sb1.add_text("main", icon="git", side="right")

        # ── Reactive (textsignal) ──────────────────────────────────────────
        with bs.Column(gap=4):
            bs.Label("Reactive (textsignal)", font="heading-sm")
            issues = bs.Signal("0 issues")
            seen = {"n": 0}

            sb2 = bs.StatusBar(horizontal="stretch")
            sb2.add_text(textsignal=issues, icon="exclamation-triangle")
            sb2.add_text("Saved", icon="cloud-check", side="right")

            def add_issue():
                seen["n"] += 1
                issues.set(f"{seen['n']} issues")

            bs.Button("Add issue", icon="plus", on_click=add_issue)

        # ── Embedded widget ────────────────────────────────────────────────
        with bs.Column(gap=4):
            bs.Label("Embedded widget", font="heading-sm")
            sb3 = bs.StatusBar(horizontal="stretch")
            sb3.add_text("Syncing", icon="arrow-repeat")
            sb3.add_widget(bs.ProgressBar, value=65)
            sb3.add_text("main", icon="git", side="right")

        # ── Surface ────────────────────────────────────────────────────────
        with bs.Column(gap=4):
            bs.Label("Card surface", font="heading-sm")
            sb4 = bs.StatusBar(horizontal="stretch", surface="card")
            sb4.add_text("Card surface", icon="layers")
            sb4.add_text("3 warnings", icon="exclamation-triangle", side="right")

app.run()
