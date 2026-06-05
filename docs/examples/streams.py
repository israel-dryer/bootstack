"""Streams — composing event pipelines with operators.

Call an ``on_*()`` shorthand with no handler to get a Stream. Chain operators
to transform, filter, and time the values, then call ``.listen()`` to attach a
handler and activate the binding.

This is a search-as-you-type box: keystrokes are mapped to the field text,
short queries are filtered out, and the search only runs once the user pauses.
"""

import bootstack as bs

with bs.App(title="Streams", padding=16, gap=8, minsize=(380, 1)) as app:
    bs.Label("Search", font="caption")
    query = bs.TextField(placeholder="Type at least 3 characters…")

    status = bs.Label("Waiting for input…", font="body")
    runs = bs.Label("Searches run: 0", font="caption")

    count = {"n": 0}

    def run_search(text: str) -> None:
        count["n"] += 1
        status.text = f"Searching for {text!r}"
        runs.text = f"Searches run: {count['n']}"

    # Build the pipeline once. Each operator returns a new Stream; `.listen()`
    # is the terminal that activates the upstream Tk binding.
    (
        query.on_input()                       # Stream of keystroke events
        .map(lambda e: e.data["text"])         # event  -> current text
        .map(str.strip)                        # trim whitespace
        .filter(lambda text: len(text) >= 3)   # ignore very short queries
        .debounce(300)                         # wait for a 300 ms pause
        .listen(run_search)                    # attach handler, bind upstream
    )

app.run()