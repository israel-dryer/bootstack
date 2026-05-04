import bootstack as bs
from bootstack import Toast

root = bs.Window()

toast = Toast()

title = "This is a really long title and probably it should not be a title if you are going to include this much text."
message = "This is a really long message and one that I think will cause the page to wrap hopefully if it gets too long."

bs.Button(
    root,
    text="Normal Toast",
    command=lambda: toast.show(
        title="bootstack",
        icon='bootstrap-fill',
        message="Hello world! This is a toast message",
        memo='Just now')
).pack(side='right', padx=20, pady=20)

bs.Button(
    root,
    text="Long Title",
    command=lambda: toast.show(
        title=title,
        icon='bootstrap-fill',
        message="Hello world! This is a toast message")
).pack(side='right', padx=20, pady=20)

bs.Button(
    root,
    text="Long Message",
    command=lambda: toast.show(
        title="bootstack",
        icon='bootstrap-fill',
        message=message)
).pack(side='right', padx=20, pady=20)

bs.Button(
    root,
    text="Message with Icon",
    command=lambda: toast.show(
        icon='bootstrap-fill',
        message="You have new messages")
).pack(side='right', padx=20, pady=20)

bs.Button(
    root,
    text="Message Only",
    command=lambda: toast.show(
        message="You have new messages",
        accent="danger")
).pack(side='right', padx=20, pady=20)

bs.Button(
    root,
    text="With Timeout",
    command=lambda: toast.show(
        message="This will only last for 2 seconds",
        duration=2000)
).pack(side='right', padx=20, pady=20)

bs.Button(
    root,
    text="Normal With Buttons",
    command=lambda: toast.show(
        title="bootstack",
        merge=False,
        icon='bootstrap-fill',
        message="Hello world! This is a toast message",
        show_close_button=False,
        alert=True,
        buttons=[{"text": "Submit", "command": lambda: print("Hello world")},
                 {"text": "Cancel", "bootstyle": "secondary"}],
        memo="Just Now")
).pack(side='right', padx=20, pady=20)

bs.Button(
    root,
    text="Primary Toast",
    command=lambda: toast.show(
        title="bootstack",
        icon='bootstrap-fill',
        message="Hello world! This is a toast message",
        accent="primary",
        position="-100+100",
        memo='Just now')
).pack(side='right', padx=20, pady=20)

root.mainloop()
