"""Toast demo — click buttons to trigger notifications."""
import bootstack as bs


def _basic():
    bs.toast("This is a simple notification.")


def _with_title():
    bs.toast("Your changes have been saved.", title="File saved", accent="success",
             icon="check-circle")


def _success():
    bs.Toast(title="Success", message="Operation completed successfully.",
             accent="success", duration=3000).show()


def _warning():
    bs.Toast(title="Low disk space",
             message="You have less than 1 GB remaining.",
             accent="warning", icon="exclamation-triangle", duration=4000).show()


def _danger():
    bs.Toast(title="Upload failed",
             message="Could not reach the server. Check your connection.",
             accent="danger", icon="x-circle", duration=5000).show()


def _info():
    bs.Toast(title="Update available",
             message="Version 2.1 is ready to install.",
             accent="info", icon="arrow-down-circle", duration=4000).show()


def _with_detail():
    bs.Toast(message="Backup completed.", detail="just now",
             accent="success", icon="cloud-check", duration=3000).show()


def _with_actions():
    bs.Toast(
        title="Delete 3 files?",
        message="This action cannot be undone.",
        accent="danger",
        show_close_button=False,
        actions=[
            {"text": "Cancel"},
            {"text": "Delete", "accent": "danger"},
        ],
    ).show()


def _persistent():
    bs.Toast(title="Action required",
             message="Review pending changes before proceeding.",
             accent="warning", duration=None).show()


with bs.App(title="Toast", minsize=(500, 500), padding=20, gap=12) as app:

    bs.Label("Simple notification", font="heading-md[bold]")
    with bs.HStack(gap=8):
        bs.Button("Basic", on_click=_basic)
        bs.Button("With title and icon", on_click=_with_title)

    bs.Label("Accent colors", font="heading-md[bold]")
    with bs.HStack(gap=8):
        bs.Button("Success", on_click=_success)
        bs.Button("Warning", on_click=_warning)
        bs.Button("Danger", on_click=_danger)
        bs.Button("Info", on_click=_info)

    bs.Label("Detail text", font="heading-md[bold]")
    bs.Button("With detail (timestamp)", on_click=_with_detail)

    bs.Label("Action buttons", font="heading-md[bold]")
    bs.Button("Confirm delete", on_click=_with_actions)

    bs.Label("Persistent (no auto-dismiss)", font="heading-md[bold]")
    bs.Button("Show persistent", on_click=_persistent)

app.run()
