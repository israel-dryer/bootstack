"""Form demo — look and feel review for bs widget composition.

Run: python tests/features/form_demo.py
"""
import bootstack as bs


class FormDemo(bs.App):
    def __init__(self):
        super().__init__(title="Create Account", minsize=(680, 760))
        self._build()

    def _build(self):
        scroll = bs.ScrollView(self)
        scroll.pack(fill="both", expand=True)
        c = scroll.add(padding=24)

        # ── Header ─────────────────────────────────────────────────────
        bs.Label(c, text="Create your account", font="heading-lg[bold]").pack(anchor="w")
        bs.Label(c, text="Fill in the details below to get started.", font="body").pack(anchor="w", pady=(4, 20))

        # ── Personal information ────────────────────────────────────────
        card1 = bs.Card(c)
        card1.pack(fill="x", pady=(0, 12))
        bs.Label(card1, text="Personal information", font="body[bold]").pack(anchor="w", pady=(0, 12))

        g1 = bs.GridFrame(card1, columns=2, gap=12, sticky_items="ew")
        g1.pack(fill="x")
        bs.TextEntry(g1, label="First name").grid()
        bs.TextEntry(g1, label="Last name").grid()
        bs.TextEntry(g1, label="Email address").grid(columnspan=2)
        bs.TextEntry(g1, label="Username").grid()
        bs.PasswordEntry(g1, label="Password").grid()

        # ── Location & language ─────────────────────────────────────────
        card2 = bs.Card(c)
        card2.pack(fill="x", pady=(0, 12))
        bs.Label(card2, text="Location & language", font="body[bold]").pack(anchor="w", pady=(0, 12))

        g2 = bs.GridFrame(card2, columns=2, gap=12, sticky_items="ew")
        g2.pack(fill="x")

        countries = ["United States", "United Kingdom", "Canada", "Australia", "Germany", "France", "Japan"]
        bs.SelectBox(g2, label="Country", enable_search=True, items=countries).grid()

        languages = ["English", "Spanish", "French", "German", "Japanese", "Portuguese"]
        bs.SelectBox(g2, label="Language", items=languages).grid()

        bs.TextEntry(g2, label="City").grid()
        bs.NumericEntry(g2, label="Age", minvalue=18, maxvalue=120).grid()

        # ── Plan ───────────────────────────────────────────────────────
        card3 = bs.Card(c)
        card3.pack(fill="x", pady=(0, 12))
        bs.Label(card3, text="Choose your plan", font="body[bold]").pack(anchor="w", pady=(0, 12))

        rg = bs.RadioGroup(card3)
        rg.add(text="Free — basic features, up to 3 projects", value="free", key="free")
        rg.add(text="Pro — all features, unlimited projects", value="pro", key="pro")
        rg.add(text="Team — collaboration + admin panel", value="team", key="team")
        rg.set("free")
        rg.pack(fill="x")

        # ── Notifications ───────────────────────────────────────────────
        card4 = bs.Card(c)
        card4.pack(fill="x", pady=(0, 12))
        bs.Label(card4, text="Notifications", font="body[bold]").pack(anchor="w", pady=(0, 12))

        sw_row = bs.PackFrame(card4, direction="row", gap=32, fill_items="none")
        sw_row.pack(anchor="w")
        bs.Switch(sw_row, text="Email").pack()
        bs.Switch(sw_row, text="SMS", value=True).pack()
        bs.Switch(sw_row, text="Browser push").pack()
        bs.Switch(sw_row, text="Marketing").pack()

        # ── Budget ──────────────────────────────────────────────────────
        card5 = bs.Card(c)
        card5.pack(fill="x", pady=(0, 12))
        bs.Label(card5, text="Budget settings", font="body[bold]").pack(anchor="w", pady=(0, 8))
        bs.Label(card5, text="Monthly spend limit", font="body").pack(anchor="w", pady=(0, 4))
        bs.Slider(card5, minvalue=0, maxvalue=500, value=100, tick_interval=100, show_value=True, tick_format="${:.0f}",
            accent="success").pack(fill="x", pady=(0, 16))

        bs.Label(card5, text="Target audience age range", font="body").pack(anchor="w", pady=(0, 4))
        bs.RangeSlider(card5, minvalue=18, maxvalue=65, lovalue=25, hivalue=45,
            show_value=True, accent="primary",
        ).pack(fill="x")

        # ── Scale vs Slider comparison ──────────────────────────────────
        card_cmp = bs.Card(c)
        card_cmp.pack(fill="x", pady=(0, 12))
        bs.Label(card_cmp, text="Scale vs Slider — size alignment check",
                 font="body[bold]").pack(anchor="w", pady=(0, 12))

        bs.Label(card_cmp, text="bs.Scale (original ttk)", font="body").pack(
            anchor="w", pady=(0, 4))
        bs.Scale(card_cmp, from_=0, to=100, value=60, orient="horizontal").pack(
            fill="x", pady=(0, 16))

        bs.Label(card_cmp, text="bs.Slider", font="body").pack(
            anchor="w", pady=(0, 4))
        bs.Slider(card_cmp, value=60).pack(fill="x")

        # ── Agreement ───────────────────────────────────────────────────
        card6 = bs.Card(c)
        card6.pack(fill="x", pady=(0, 24))
        bs.CheckButton(card6, text="I agree to the Terms of Service and Privacy Policy").pack(anchor="w", pady=(0, 8))
        bs.CheckButton(card6, text="I confirm I am 18 years of age or older").pack(anchor="w")

        # ── Actions ─────────────────────────────────────────────────────
        actions = bs.PackFrame(c, direction="row", gap=8)
        actions.pack(fill="x")
        bs.Button(actions, text="Cancel", variant="ghost").pack(side="left", expand=True, anchor='w')
        bs.Button(actions, text="Save draft", variant="outline").pack()
        bs.Button(actions, text="Create account", icon="person-plus", accent="primary").pack()


if __name__ == "__main__":
    FormDemo().mainloop()