import bootstack as bs


def hero():
    with bs.App(title="Toast", size=(440, 80), padding=0) as app:
        def show_toast():
            bs.Toast(
                message="Your files have been saved.",
                duration=8000,
                position="+212+141",
            ).show()
        app.tk.after(850, show_toast)
    app.run()


def accents():
    with bs.App(title="Toast — Accents", size=(440, 320), padding=0) as app:
        def show_toasts():
            for i, (accent, title, icon) in enumerate([
                ("info",    "Update available", "info-circle"),
                ("success", "Changes saved",    "check-circle"),
                ("warning", "Storage is low",   "exclamation-triangle"),
                ("danger",  "Upload failed",    "x-circle"),
            ]):
                bs.Toast(
                    title=title,
                    accent=accent,
                    icon=icon,
                    duration=8000,
                    position=f"+212+{141 + i * 78}",
                ).show()
        app.tk.after(850, show_toasts)
    app.run()


def actions():
    with bs.App(title="Toast — Actions", size=(440, 180), padding=0) as app:
        def show_toast():
            bs.Toast(
                title="Delete 3 files?",
                message="This action cannot be undone.",
                show_close_button=False,
                actions=[
                    {"text": "Cancel"},
                    {"text": "Delete", "accent": "danger"},
                ],
                duration=8000,
                position="+212+141",
            ).show()
        app.tk.after(850, show_toast)
    app.run()


SCENES = {
    "hero":    hero,
    "accents": accents,
    "actions": actions,
}