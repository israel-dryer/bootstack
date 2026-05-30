"""Form demo — look and feel review using the public API.

Run: python tests/features/form_demo.py
"""
import bootstack as bs

with bs.App(title="Create Account", size=(680, 760)) as app:
    with bs.ScrollView(fill="both", expand=True):
        with bs.VStack(padding=24, gap=12, fill="horizontal", fill_items="horizontal"):

            # ── Header ─────────────────────────────────────────────────
            bs.Label("Create your account", font="heading-lg[bold]")
            bs.Label("Fill in the details below to get started.", font="body")

            # ── Personal information ────────────────────────────────────
            with bs.Card(gap=12, fill_items="horizontal"):
                bs.Label("Personal information", font="body[bold]")
                with bs.Grid(columns=2, gap=12, sticky_items="ew"):
                    bs.TextField(label="First name")
                    bs.TextField(label="Last name")
                    bs.TextField(label="Email address", columnspan=2)
                    bs.TextField(label="Username")
                    bs.PasswordField(label="Password")

            # ── Location & language ─────────────────────────────────────
            with bs.Card(gap=12, fill_items="horizontal"):
                bs.Label("Location & language", font="body[bold]")
                with bs.Grid(columns=2, gap=12, sticky_items="ew"):
                    countries = ["United States", "United Kingdom", "Canada",
                                 "Australia", "Germany", "France", "Japan"]
                    bs.Select(label="Country", options=countries, allow_custom_values=True)

                    languages = ["English", "Spanish", "French", "German",
                                 "Japanese", "Portuguese"]
                    bs.Select(label="Language", options=languages)

                    bs.TextField(label="City")
                    bs.NumberField(label="Age", min_value=18, max_value=120)

            # ── Plan ───────────────────────────────────────────────────
            with bs.Card(gap=8, fill_items="horizontal"):
                bs.Label("Choose your plan", font="body[bold]")
                rg = bs.RadioGroup(orient="vertical")
                rg.add("Free — basic features, up to 3 projects", value="free")
                rg.add("Pro — all features, unlimited projects", value="pro")
                rg.add("Team — collaboration + admin panel", value="team")
                rg.value = "free"

            # ── Notifications ───────────────────────────────────────────
            with bs.Card(gap=8):
                bs.Label("Notifications", font="body[bold]")
                with bs.HStack(gap=32):
                    bs.Switch("Email")
                    bs.Switch("SMS", value=True)
                    bs.Switch("Browser push")
                    bs.Switch("Marketing")

            # ── Budget ─────────────────────────────────────────────────
            with bs.Card(gap=8, fill_items="horizontal"):
                bs.Label("Budget settings", font="body[bold]")
                bs.Label("Monthly spend limit", font="body")
                bs.Slider(
                    min_value=0, max_value=500, value=100,
                    tick_step=100, show_value=True,
                    tick_format="${:.0f}", accent="success",
                )
                bs.Label("Target audience age range", font="body")
                bs.RangeSlider(
                    min_value=18, max_value=65,
                    low_value=25, high_value=45,
                    show_value=True, accent="primary",
                )

            # ── Agreement ───────────────────────────────────────────────
            with bs.Card(gap=8, fill_items='horizontal'):
                bs.Checkbox("I agree to the Terms of Service and Privacy Policy")
                bs.Checkbox("I confirm I am 18 years of age or older")

            # ── Actions ─────────────────────────────────────────────────
            with bs.HStack(gap=8, fill="horizontal"):
                bs.Button("Cancel", variant="ghost", expand=True, anchor="w")
                bs.Button("Save draft", variant="outline")
                bs.Button("Create account", icon="person-plus", accent="primary")

app.run()